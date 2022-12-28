from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

GROUP_NAMES = {
    'AD': 'Administrator',
    'PM': 'Project Manager',
    'DV': 'Developer',
    'SM': 'Submitter',
}

def set_user_group_from_role(user):
    group, created = Group.objects.get_or_create(name=GROUP_NAMES[user.user_role])
    # add permissions if group is newly created
    if created:
        add_group_permissions(group)
    # remove all user groups
    user.groups.clear()
    # assign specific group based on role 
    user.groups.add(group)
    

# Get content types:
project_content = ContentType.objects.get(app_label='pages', model='project')
ticket_content = ContentType.objects.get(app_label='pages', model='ticket')
history_content = ContentType.objects.get(app_label='pages', model='tickethistory')
comment_content = ContentType.objects.get(app_label='pages', model='ticketcomment')
ticketfiles_content = ContentType.objects.get(app_label='pages', model='ticketfiles')
user_content = ContentType.objects.get(app_label='accounts', model='customuser')
# Build permissions
add_project, _ = Permission.objects.get_or_create(
    codename='add_project',
    name='Can add project',
    content_type=project_content)
add_ticket, _ = Permission.objects.get_or_create(
    codename='add_ticket',
    name='Can add ticket',
    content_type=ticket_content)
add_history, _ = Permission.objects.get_or_create(
    codename='add_history',
    name='Can add history',
    content_type=history_content)
add_comment, _ = Permission.objects.get_or_create(
    codename='add_comment',
    name='Can add comment',
    content_type=comment_content)
view_project, _ = Permission.objects.get_or_create(
    codename='view_project',
    name='Can view project',
    content_type=project_content)
view_ticket, _ = Permission.objects.get_or_create(
    codename='view_ticket',
    name='Can view ticket',
    content_type=ticket_content)
view_history, _ = Permission.objects.get_or_create(
    codename='view_history',
    name='Can view history',
    content_type=history_content)
view_comment, _ = Permission.objects.get_or_create(
    codename='view_comment',
    name='Can view comment',
    content_type=comment_content)
add_ticketfiles, _ = Permission.objects.get_or_create(
    codename='add_ticketfiles',
    name='Can add ticket files',
    content_type=ticketfiles_content)
change_ticketfiles, _ = Permission.objects.get_or_create(
    codename='change_ticketfiles',
    name='Can change ticket files',
    content_type=ticketfiles_content)
delete_ticketfiles, _ = Permission.objects.get_or_create(
    codename='delete_ticketfiles',
    name='Can delete ticket files',
    content_type=ticketfiles_content)
view_ticketfiles, _ = Permission.objects.get_or_create(
    codename='view_ticketfiles',
    name='Can view ticket files',
    content_type=ticketfiles_content)
change_user, _ = Permission.objects.get_or_create(
    codename='change_user',
    name='Can change user',
    content_type=user_content)
view_user, _ = Permission.objects.get_or_create(
    codename='view_user',
    name='Can view user',
    content_type=user_content)
change_project, _ = Permission.objects.get_or_create(
    codename='change_project',
    name='Can change project',
    content_type=project_content)
change_ticket, _ = Permission.objects.get_or_create(
    codename='change_ticket',
    name='Can change ticket',
    content_type=ticket_content)
delete_project, _ = Permission.objects.get_or_create(
    codename='delete_project',
    name='Can delete project',
    content_type=project_content)
# Assign Permissions
admin_perms = [
    change_user,
    view_user,
    add_project,
    change_project,
    view_project,
    change_ticket,
    view_ticket,
    add_ticketfiles,
    change_ticketfiles,
    delete_ticketfiles,
    view_ticketfiles,
    add_comment,
    view_comment
    
]

pm_perms = [
    add_project,
    change_project,
    delete_project,
    view_project,
    change_ticket,
    view_ticket,
    add_comment,
    view_comment,
    add_ticketfiles,
    view_ticketfiles,
    change_ticketfiles
]

dev_perms = [
    view_project,
    view_ticket,
    add_ticketfiles,
    view_ticketfiles,
    add_comment,
    view_comment
    
]

sub_perms = [
    view_project,
    add_ticket,
    view_ticket,
    add_ticketfiles,
    add_comment

]

name_to_perms = {
    'Administrator': admin_perms,
    'Project Manager': pm_perms,
    'Developer': dev_perms,
    'Submitter': sub_perms
}

def add_group_permissions(group):
    name = group.name
    
    for perm in name_to_perms[name]:
        group.permissions.add(perm)
