from django.test import TestCase
from unittest import skipIf
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from openfga_sdk.client.models import (
    ClientCheckRequest,
    ClientBatchCheckRequest,
    ClientBatchCheckItem,
    ClientWriteRequest,
    ClientTuple,
)

from services.openfga.sync import client as ofga
from services.openfga.settings import configuration as ofga_config
from services.openfga.relations import (
    ContentNodeRelation,
    CourseClassRelation,
    UserRelation,
)
from courses.models import Course, CourseClass
from enrollment.models import Enrollment, EnrollmentRole

from ..models import ContentNode, Module, Lesson

User = get_user_model()


@skipIf(not ofga_config.api_url or not ofga_config.store_id, "OpenFGA not configured")
class ContentNodeAuthzSyncTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass", is_active=True
        )
        self.course = Course.objects.create(name="C1", description="D")
        self.course_class = CourseClass.objects.create(
            name="C1-A", course=self.course, is_open=False
        )

        self.module_ct = ContentType.objects.get_for_model(Module)
        self.lesson_ct = ContentType.objects.get_for_model(Lesson)

        # Module and Lesson only have a 'content' field
        self.module = Module.objects.create(content="M1")
        self.lesson = Lesson.objects.create(content="L1")

        self.root_node = ContentNode.objects.create(
            title="RootNode",
            course_class=self.course_class,
            order=1,
            content_type=self.module_ct,
            object_id=self.module.id,
        )
        self.lesson_node = ContentNode.objects.create(
            title="LessonNode",
            course_class=self.course_class,
            order=1,
            content_type=self.lesson_ct,
            object_id=self.lesson.id,
            parent=self.root_node,
        )

    def test_node_course_class_sync(self):
        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    ClientBatchCheckItem(
                        user=f"{CourseClassRelation.TYPE}:{self.course_class.id}",
                        relation=ContentNodeRelation.COURSE_CLASS,
                        object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                    ),
                    ClientBatchCheckItem(
                        user=f"{CourseClassRelation.TYPE}:{self.course_class.id}",
                        relation=ContentNodeRelation.COURSE_CLASS,
                        object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
                    ),
                ]
            )
        )
        self.assertTrue(all(item.allowed for item in res.result))

    def test_node_parent_sync(self):
        res = ofga.check(
            ClientCheckRequest(
                user=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                relation=ContentNodeRelation.PARENT,
                object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
            )
        ).allowed
        self.assertTrue(res)

    def test_lesson_node_on_delete_sync(self):
        to_check = [
            ClientBatchCheckItem(
                user=f"{CourseClassRelation.TYPE}:{self.course_class.id}",
                relation=ContentNodeRelation.COURSE_CLASS,
                object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
            ),
            ClientBatchCheckItem(
                user=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                relation=ContentNodeRelation.PARENT,
                object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
            ),
        ]
        res = ofga.batch_check(ClientBatchCheckRequest(checks=to_check))
        self.assertTrue(all(item.allowed for item in res.result))

        self.lesson_node.delete()

        # After deletion, the relation should no longer exist
        res = ofga.batch_check(ClientBatchCheckRequest(checks=to_check))
        self.assertTrue(all(not item.allowed for item in res.result))

    def test_user_can_view_node_forbidden(self):
        can_view = ofga.check(
            ClientCheckRequest(
                user=f"{UserRelation.TYPE}:{self.user.id}",
                relation=ContentNodeRelation.CAN_VIEW,
                object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
            )
        ).allowed
        self.assertFalse(can_view)

    def test_user_can_view_node_allowed(self):
        Enrollment.objects.create(
            user=self.user, course_class=self.course_class, role=EnrollmentRole.STUDENT
        )
        can_view = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_VIEW,
                        object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                    ),
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_VIEW,
                        object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
                    ),
                ]
            )
        )
        self.assertTrue(all(item.allowed for item in can_view.result))

    def test_teacher_can_modify_all_nodes(self):
        Enrollment.objects.create(
            user=self.user, course_class=self.course_class, role=EnrollmentRole.TEACHER
        )
        can_modify = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_MODIFY,
                        object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                    ),
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_MODIFY,
                        object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
                    ),
                ]
            )
        )
        self.assertTrue(all(item.allowed for item in can_modify.result))

    def test_share_node_view_permission(self):
        ofga.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.VIEWER,
                        object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                    )
                ]
            )
        )
        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_VIEW,
                        object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                    ),
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_VIEW,
                        object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
                    ),
                ]
            )
        )
        self.assertTrue(all(item.allowed for item in res.result))

    def test_share_node_edit_permission(self):
        ofga.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.EDITOR,
                        object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                    )
                ]
            )
        )
        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_EDIT,
                        object=f"{ContentNodeRelation.TYPE}:{self.root_node.id}",
                    ),
                    ClientBatchCheckItem(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=ContentNodeRelation.CAN_EDIT,
                        object=f"{ContentNodeRelation.TYPE}:{self.lesson_node.id}",
                    ),
                ]
            )
        )
        self.assertTrue(all(item.allowed for item in res.result))
