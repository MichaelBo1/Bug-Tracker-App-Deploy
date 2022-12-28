from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .helpers import add_history
from .models import Project, Ticket



@receiver(post_save, sender=Project)
def close_project_tickets_if_archived(sender, instance, created, **kwargs):
    # runs only if project is being updated
    if not created and not instance.is_active:
        for ticket in instance.tickets.all():
            ticket.status = 'CLOSED'
            ticket.save()


@receiver(pre_save, sender=Ticket)
def record_ticket_history(sender, instance, raw, **kwargs):
    # do nothing if ticket instance is being created
    if not raw and instance.id:
        previous_state = Ticket.objects.get(id=instance.id)
        
        if previous_state.assigned_developer != instance.assigned_developer:
            add_history(
                action='Assigned to User', 
                prev_val=previous_state.assigned_developer,
                new_val=instance.assigned_developer,
                ticket=instance)

        if previous_state.status != instance.status:
            add_history(
                action='Status Updated', 
                prev_val=previous_state.status,
                new_val=instance.status,
                ticket=instance)

        if previous_state.priority != instance.priority:
            add_history(
                action='Priority Changed', 
                prev_val=previous_state.priority,
                new_val=instance.priority,
                ticket=instance)
            
        if previous_state.type != instance.type:
            add_history(
                action='Type Changed',
                prev_val=previous_state.type,
                new_val=instance.type,
                ticket=instance
            )