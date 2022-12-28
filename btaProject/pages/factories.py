import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from factory.django import DjangoModelFactory

from . import models

class ContentTypeFactory(DjangoModelFactory):
    class Meta:
        model = ContentType
        django_get_or_create = ('app_label', 'model')

    app_label = factory.Faker("word")
    model = factory.Faker("word")


class PermissionFactory(DjangoModelFactory):
    class Meta:
        model = Permission
        django_get_or_create = ('name', 'codename')

    name = factory.Faker("name")
    codename = factory.Faker('codename')
    content_type = factory.SubFactory(ContentTypeFactory)


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ("name",)

    name = factory.Faker("name")

class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = factory.Faker('username')

class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = models.Project
        django_get_or_create = ('title', 'description')

    title = factory.Faker('title')
    description = factory.Faker('description')

class TicketFactory(DjangoModelFactory):
    class Meta:
        model = models.Ticket
        django_get_or_create = ('title', 'description', 'project', 'submitter')

    title = factory.Faker('title')
    description = factory.Faker('description')
    priority = 'MEDIUM'
    status = 'OPEN'
    type = 'CHANGE'
    submitter  = factory.SubFactory(CustomUserFactory)
    project = factory.SubFactory(ProjectFactory)
