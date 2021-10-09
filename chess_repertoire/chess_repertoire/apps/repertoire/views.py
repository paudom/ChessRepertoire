from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import (CreateView, DetailView, ListView, UpdateView, TemplateView)

from .constants import MAX_OPENING_PER_PAGE
from .models import Opening, Variation
from .forms import OpeningForm
from .filters import OpeningFilter

# -- General Views -- #
class AboutPage(TemplateView):
    template_name = 'repertoire/about.html'

# -- Opening Views -- #
class OpeningIndex(ListView):
    model = Opening
    paginate_by = MAX_OPENING_PER_PAGE
    context_object_name = 'openings'
    template_name = 'repertoire/openings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = OpeningFilter(self.request.GET, queryset=self.get_queryset())
        return context

class OpeningDetail(DetailView):
    model = Opening
    template_name = 'repertoire/opening_detail.html'
    context_object_name = 'opening'

class NewOpening(CreateView):
    model = Opening
    form_class = OpeningForm
    template_name = 'repertoire/opening_form.html'

class ModifyOpening(UpdateView):
    model = Opening
    form_class = OpeningForm
    template_name = 'repertoire/opening_form.html'

# -- Variation Views -- #