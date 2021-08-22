from django.urls import path
from . import views

urlpatterns = [
    path('', views.OpeningIndex.as_view(), name='openings'),
    path('<str:name>/', views.OpeningDetail.as_view(), name='opening')
]