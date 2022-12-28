from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Q

from ..forms import ManageProjectUsersForm, TicketUpdateForm, UserRolesForm

class UserRolesFormTests(TestCase):
    def setUp(self):
        self.form = UserRolesForm()
        return super().setUp()

    def test_users_field_qs_excludes_superusers(self):
        """Returns true if queryset excludes superusers"""
        qs = get_user_model().objects.exclude(is_superuser=True)
        self.assertQuerysetEqual(self.form.fields['users'].queryset, qs)

class TicketUpdateFormTests(TestCase):
    def test_assigned_developer_query_set_includes_only_developers(self):
        """Returns true if queryset includes only users who are developers"""
        form = TicketUpdateForm()
        dev_qs = get_user_model().objects.filter(is_superuser=False, user_role='DV')
        self.assertQuerysetEqual(form.fields['assigned_developer'].queryset, dev_qs)


class ManageProjectUsersFormTests(TestCase):
    def setUp(self):
        self.form = ManageProjectUsersForm()
        return super().setUp()

    def test_assigned_personnel_queryset_excludes_admins_and_project_managers(self):
        """Returns true if query set includes only developers and submitters"""
        filtered_qs = get_user_model().objects.exclude(Q(is_superuser=True) | Q(user_role__in=['AD', 'PM']))
        self.assertQuerysetEqual(self.form.fields['assigned_personnel'].queryset, filtered_qs)

    def test_project_manager_queryset_includes_only_project_managers(self):
        """Returns true if query set only includes project managers"""
        pm_queryset = get_user_model().objects.filter(user_role='PM')
        self.assertQuerysetEqual(self.form.fields['project_manager'].queryset, pm_queryset)

