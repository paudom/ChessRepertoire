from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Opening, Variation

from src.constants import MAX_PER_PAGE

# -- Opening Views -- #
class OpeningList(ListView):
    model = Opening
    paginate_by = MAX_PER_PAGE
    context_object_name = 'openings'

class OpeningDetail(DetailView):
    model = Opening
    context_object_name = 'variations'

# -- Variation Views -- #


# -- Other Views -- #
