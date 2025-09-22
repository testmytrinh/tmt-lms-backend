from django.test import TestCase
from unittest import skipIf
from django.db.models import signals
from openfga_sdk.client.models import (
    ClientBatchCheckRequest,
    ClientBatchCheckItem,
)
from functools import partial

from services.openfga.sync import client as ofga
from services.openfga.settings import configuration as ofga_config
from services.openfga.relations import CourseClassRelation, UserRelation

from ..models import Enrollment, EnrollmentRole
from ..signals import sync_enrollment_to_fga
from courses.models import Course, CourseClass
from django.contrib.auth import get_user_model

User = get_user_model()


@skipIf(not ofga_config.api_url or not ofga_config.store_id, "OpenFGA not configured")
class EnrollmentAuthzSyncTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        signals.post_save.connect(
            sync_enrollment_to_fga,
            dispatch_uid="sync_enrollment_to_fga",
            sender=Enrollment,
        )
        return super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(
            email="u@example.com", password="pass123", is_active=True
        )
        self.course = Course.objects.create(name="C1", description="D")
        self.course_class = CourseClass.objects.create(name="C1-A", course=self.course)
        self.make_check_item = partial(
            ClientBatchCheckItem,
            user=f"{UserRelation.TYPE}:{self.user.id}",
            object=f"{CourseClassRelation.TYPE}:{self.course_class.id}",
        )

    def test_teacher_sync(self):
        Enrollment.objects.create(
            user=self.user, course_class=self.course_class, role=EnrollmentRole.TEACHER
        )
        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    self.make_check_item(relation=CourseClassRelation.TEACHER),
                    self.make_check_item(relation=CourseClassRelation.CAN_MODIFY),
                    self.make_check_item(relation=CourseClassRelation.CAN_EDIT),
                    self.make_check_item(relation=CourseClassRelation.CAN_VIEW),
                ]
            )
        ).result

        self.assertTrue(all(item.allowed for item in res))

    def test_student_sync(self):
        Enrollment.objects.create(
            user=self.user, course_class=self.course_class, role=EnrollmentRole.STUDENT
        )
        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    self.make_check_item(
                        relation=CourseClassRelation.STUDENT, correlation_id="1"
                    ),
                    self.make_check_item(
                        relation=CourseClassRelation.CAN_VIEW, correlation_id="2"
                    ),
                    self.make_check_item(
                        relation=CourseClassRelation.CAN_EDIT, correlation_id="3"
                    ),
                    self.make_check_item(
                        relation=CourseClassRelation.CAN_MODIFY, correlation_id="4"
                    ),
                ]
            )
        ).result

        find_item = partial(
            lambda corr_id, items: next(
                i for i in items if i.correlation_id == corr_id
            ).allowed,
            items=res,
        )
        self.assertTrue(find_item("1"))  # Student
        self.assertTrue(find_item("2"))  # Can View
        self.assertFalse(find_item("3"))  # Cannot Edit
        self.assertFalse(find_item("4"))  # Cannot Modify

    def test_guest_sync(self):
        Enrollment.objects.create(
            user=self.user, course_class=self.course_class, role=EnrollmentRole.GUEST
        )
        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    self.make_check_item(
                        relation=CourseClassRelation.GUEST, correlation_id="0"
                    ),
                    self.make_check_item(
                        relation=CourseClassRelation.CAN_VIEW, correlation_id="1"
                    ),
                    self.make_check_item(
                        relation=CourseClassRelation.CAN_EDIT, correlation_id="2"
                    ),
                    self.make_check_item(
                        relation=CourseClassRelation.CAN_MODIFY, correlation_id="3"
                    ),
                ]
            )
        ).result

        find_item = partial(
            lambda corr_id, items: next(
                i for i in items if i.correlation_id == corr_id
            ).allowed,
            items=res,
        )
        self.assertTrue(find_item("0"))  # Guest
        self.assertTrue(find_item("1"))  # Can View
        self.assertFalse(find_item("2"))  # Cannot Edit
        self.assertFalse(find_item("3"))  # Cannot Modify
