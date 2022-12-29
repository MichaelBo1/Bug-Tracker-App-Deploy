from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.DemoLoginView.as_view(), name='demo_login'),
]