from django.urls import path

from . import views

app_name = 'repertoire'

urlpatterns = [
    path('', views.OpeningIndex.as_view(), name='openings'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('new_opening/', views.NewOpening.as_view(), name='new_opening'),
    path('<slug:slug>/', views.OpeningDetail.as_view(), name='opening_detail'),
    path('<slug:slug>/modify/', views.ModifyOpening.as_view(), name='modify_opening'),
    path('<slug:slug>/variations/', views.OpeningVariations.as_view(), name='opening_variations'),
    path('<slug:slug>/new_variation/', views.NewVariation.as_view(), name='new_variation'),
    path('<str:opn>/<slug:slug>/modify/', views.ModifyVariation.as_view(), name='modify_variation'),
    path('<str:opn>/<slug:slug>/review/', views.ReviewVariation.as_view(), name='review'),
    path('<str:opn>/<slug:slug>/practice/', views.PracticeVariation.as_view(), name='practice')
]
