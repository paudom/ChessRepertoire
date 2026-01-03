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
    path('<str:opn>/<slug:slug>/practice/', views.PracticeVariation.as_view(), name='practice'),
    # AJAX endpoints for drag-and-drop practice mode
    path('<str:opn>/<slug:slug>/practice/validate_move/', views.PracticeValidateMove.as_view(), name='practice_validate_move'),
    path('<str:opn>/<slug:slug>/practice/get_position/', views.PracticeGetPosition.as_view(), name='practice_get_position'),
    path('<str:opn>/<slug:slug>/practice/get_hints/', views.PracticeGetHints.as_view(), name='practice_get_hints'),
    path('<str:opn>/<slug:slug>/practice/restart/', views.PracticeRestart.as_view(), name='practice_restart')
]
