# coding: utf-8
from __future__ import unicode_literals, print_function, division, absolute_import
import unittest

from django.core.urlresolvers import reverse
from guardian.shortcuts import assign_perm, remove_perm

from onadata.apps.main.tests.test_base import TestBase
from onadata.apps.viewer.views import data_view


class TestDataView(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._create_user_and_login()
        self._publish_transportation_form_and_submit_instance()
        self.url = reverse(data_view, kwargs={
            'username': self.user.username,
            'id_string': self.xform.id_string
        })

    def test_data_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @unittest.skip('Fails under Django 1.6')
    def test_data_view_with_username_and_id_string_in_uppercase(self):
        url = reverse(data_view, kwargs={
            'username': self.user.username.upper(),
            'id_string': self.xform.id_string.upper()
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_restrict_for_anon(self):
        response = self.anon.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_restrict_for_not_owner(self):
        self._create_user_and_login('alice')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_allow_if_shared(self):
        self.xform.shared_data = True
        self.xform.save()
        response = self.anon.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_allow_if_user_given_permission(self):
        self._create_user_and_login('alice')
        assign_perm('change_xform', self.user, self.xform)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_disallow_if_user_permission_revoked(self):
        self._create_user_and_login('alice')
        assign_perm('change_xform', self.user, self.xform)
        response = self.client.get(self.url)
        remove_perm('change_xform', self.user, self.xform)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
