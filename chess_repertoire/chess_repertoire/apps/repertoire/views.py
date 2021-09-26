from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import MAX_PER_PAGE
from .models import Opening, Variation


# -- Opening Views -- #
class OpeningIndex(ListView):
    model = Opening
    paginate_by = MAX_PER_PAGE
    context_object_name = 'openings'
    template_name = 'repertoire/openings.html'

class OpeningDetail(DetailView):
    model = Opening
    template_name = 'repertoire/opening_detail.html'
    context_object_name = 'opening'

# -- Variation Views -- #