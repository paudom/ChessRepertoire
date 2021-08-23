from django.urls import path

from . import views

app_name = 'repertoire'

urlpatterns = [
    path('', views.OpeningIndex.as_view(), name='openings'),
    path('<str:pk>/', views.OpeningDetail.as_view(), name='opening_detail')
]
