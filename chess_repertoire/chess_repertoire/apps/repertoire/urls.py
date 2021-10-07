from django.urls import path

from . import views

app_name = 'repertoire'

urlpatterns = [
    path('', views.OpeningIndex.as_view(), name='openings'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('new_opening/', views.NewOpening.as_view(), name='new_opening'),
    path('<str:pk>/', views.OpeningDetail.as_view(), name='opening_detail'),
    path('<str:pk>/modify/', views.ModifyOpening.as_view(), name='modify_opening')
]
