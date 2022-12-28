from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    is_demo = models.BooleanField(default=False)

    class Roles(models.TextChoices):
        ADMINISTRATOR = 'AD', _('Administrator')
        PROJECT_MANAGER = 'PM', _('Project Manager')
        DEVELOPER = 'DV', _('Developer')
        SUBMITTER = 'SM', _('Submitter')

    user_role = models.CharField(max_length=2, choices=Roles.choices, default=Roles.SUBMITTER)


    def __str__(self):
        return self.email