from .models import TicketHistory
from django.utils import timezone


def add_history(action, prev_val, new_val, ticket):
    new_history = TicketHistory(
        action=action, 
        prev_value=prev_val, 
        new_value=new_val,
        date_changed=timezone.now(), 
        ticket=ticket)
    new_history.save()
