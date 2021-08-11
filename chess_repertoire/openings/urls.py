from django.urls import path

from . import views

urlpatterns = [
    path('', views.openings_home, name='openings_home'),
]