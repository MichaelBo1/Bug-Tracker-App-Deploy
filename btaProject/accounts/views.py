from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import DemoLoginForm


class DemoLoginView(FormView):
    form_class = DemoLoginForm
    template_name = 'account/demo_login.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        # Authenticate the user on demo account
        demo_user = form.cleaned_data['demo_user']
        user = authenticate(self.request, username=demo_user)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        
        else:
            # If the user is not authenticated, render the error template
            return render(self.request, 'account/acc_error.html')