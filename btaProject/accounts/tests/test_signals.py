from django.test import TestCase

from pages import factories


class AssignUserToGroupReceiverTests(TestCase):
    fixtures = ['auth.json']
    def setUp(self):
        self.user = factories.CustomUserFactory(username='test@_user')
        return super().setUp()

    def test_user_group_is_submitter_by_default(self):
        """Returns true is user belongs to Submitter group by default"""
        self.assertTrue(self.user.groups.filter(name='Submitter').exists())

    def test_user_group_is_admin_when_role_changes(self):
        """Returns true if user is added to Administrator group when user_role changes"""
        self.user.user_role = 'AD'
        self.user.save()
        self.assertTrue(self.user.groups.filter(name='Administrator').exists())

    def test_user_group_is_developer_when_role_changes(self):
        """Returns true if user is added to Developer group when user_role changes"""
        self.user.user_role = 'DV'
        self.user.save()
        self.assertTrue(self.user.groups.filter(name='Developer').exists())

    def test_user_group_is_project_manager_when_role_changes(self):
        """Returns true if user is added to Project Manager group when user_role changes"""
        self.user.user_role = 'PM'
        self.user.save()
        self.assertTrue(self.user.groups.filter(name='Project Manager').exists())
    