from django.urls import path

from . import views

app_name = 'repertoire'

urlpatterns = [
    path('', views.OpeningIndex.as_view(), name='openings'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('new_opening/', views.NewOpening.as_view(), name='new_opening'),
    path('<str:pk>/', views.OpeningDetail.as_view(), name='opening_detail'),
    path('<str:pk>/modify/', views.ModifyOpening.as_view(), name='modify_opening'),
    path('<str:pk>/variations/', views.OpeningVariations.as_view(), name='opening_variations'),
    path('<str:pk>/new_variation/', views.NewVariation.as_view(), name='new_variation'),
    path('<str:opening_name>/<str:pk>/modify/', views.ModifyVariation.as_view(), name='modify_variation'),
    path('<str:opening_name>/<str:pk>/review/', views.ReviewVariation.as_view(), name='review'),
    path('<str:opening_name>/<str:pk>/practice/', views.PracticeVariation.as_view(), name='practice')
]
