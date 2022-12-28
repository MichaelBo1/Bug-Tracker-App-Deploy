from django.contrib import admin

from .models import Project, Ticket, TicketComment, TicketFiles

admin.site.register(Project)
admin.site.register(Ticket)
admin.site.register(TicketComment)
admin.site.register(TicketFiles)