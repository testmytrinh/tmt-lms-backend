from django.test import TestCase
from unittest import skipIf
from django.db.models import signals
from django.contrib.auth.models import Group
from openfga_sdk.client.models import (
    ClientListObjectsRequest,
)

from services.openfga.sync import client as ofga
from services.openfga.settings import configuration as ofga_config
from services.openfga.relations import UserRelation, GroupRelation

from ..signals import sync_user_groups_on_changed, cleanup_user_in_fga
from ..models import User


@skipIf(not ofga_config.api_url or not ofga_config.store_id, "OpenFGA not configured")
class UserGroupMembershipSyncTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        (
            signals.m2m_changed.connect(
                sync_user_groups_on_changed,
                dispatch_uid="sync_user_groups_on_changed",
                sender=User.groups.through,
            ),
        )
        signals.pre_delete.connect(
            cleanup_user_in_fga,
            dispatch_uid="cleanup_user_in_fga",
            sender=User,
        )
        return super().setUpClass()

    def setUp(self):
        self.group1 = Group.objects.create(name="Group1")
        self.group2 = Group.objects.create(name="Group2")

    def tearDown(self):
        self.group1.delete()
        self.group2.delete()
        return super().tearDown()

    def _ofga_list_user_groups(self, user_id):
        list_objs = list(
            ofga.streamed_list_objects(
                ClientListObjectsRequest(
                    user=f"{UserRelation.TYPE}:{user_id}",
                    relation=GroupRelation.MEMBER,
                    type=GroupRelation.TYPE,
                )
            )
        )
        return [obj.object for obj in list_objs]

    def test_sync_user_groups_on_changed(self):
        user = User.objects.create_user(
            email="user@example.com", password="testpass123", is_active=True
        )
        pre_check_len = len(self._ofga_list_user_groups(user.id))
        self.assertEqual(pre_check_len, 0)
        # Add user to groups
        user.groups.add(self.group1, self.group2)
        user.save()

        # Check membership in OpenFGA
        ofga_groups_keys = self._ofga_list_user_groups(user.id)
        post_check_len = len(ofga_groups_keys)
        self.assertEqual(post_check_len, 2)
        self.assertIn(f"{GroupRelation.TYPE}:{self.group1.id}", ofga_groups_keys)
        self.assertIn(f"{GroupRelation.TYPE}:{self.group2.id}", ofga_groups_keys)

        # delete user
        user_id = user.id
        user.delete()
        post_check_len = len(self._ofga_list_user_groups(user_id))
        self.assertEqual(post_check_len, 0)
        self.assertEqual(self._ofga_list_user_groups(user_id), [])
