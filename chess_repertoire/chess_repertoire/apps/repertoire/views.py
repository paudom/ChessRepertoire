from django.views.generic import (CreateView, DetailView, ListView, UpdateView, TemplateView)
from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.safestring import mark_safe

from chess_repertoire.apps.game import ChessReviewer, ChessPractice
from .constants import MAX_OPENING_PER_PAGE, MAX_VARIATION_PER_PAGE
from .models import Opening, Variation
from .forms import OpeningForm, VariationForm
from .filters import OpeningFilter

# -- General Views -- #
class AboutPage(TemplateView):
    template_name = 'repertoire/about.html'


# -- Opening Views -- #
class OpeningIndex(ListView):
    model = Opening
    paginate_by = MAX_OPENING_PER_PAGE
    template_name = 'repertoire/openings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = OpeningFilter(self.request.GET, queryset=self.get_queryset())
        # -- Pagination with Filtering -- #
        paginator = Paginator(context['filter'].qs, OpeningIndex.paginate_by)
        page_number = self.request.GET.get('page')
        openings = paginator.get_page(page_number)
        context['openings'] = openings
        return context


class OpeningDetail(DetailView):
    model = Opening
    template_name = 'repertoire/opening_detail.html'
    context_object_name = 'opening'


class NewOpening(CreateView):
    model = Opening
    form_class = OpeningForm
    template_name = 'repertoire/opening_new_form.html'


class ModifyOpening(UpdateView):
    model = Opening
    form_class = OpeningForm
    template_name = 'repertoire/opening_modify_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opening'] = Opening.objects.get(pk=self.kwargs['pk'])
        return context


# -- Variation Views -- #
class OpeningVariations(ListView):
    model = Opening
    template_name = 'repertoire/opening_variations.html'
    paginate_by = MAX_VARIATION_PER_PAGE
    context_object_name = 'variations'

    def dispatch(self, request, *args, **kwargs):
        # -- Reset current moves -- #
        self.request.session.flush()
        if not self.request.session.get('moves', None):
            self.request.session['moves'] = []
        if not self.request.session.get('turn', None):
            self.request.session['turn'] = False
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        opening = Opening.objects.get(pk=self.kwargs['pk'])
        variations = opening.variation_set.all()
        return variations
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opening'] = Opening.objects.get(pk=self.kwargs['pk'])
        return context


class NewVariation(CreateView):
    model = Variation
    form_class = VariationForm
    template_name = 'repertoire/variation_new_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opening'] = Opening.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.opening = Opening.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)


class ModifyVariation(UpdateView):
    model = Variation
    form_class = VariationForm
    template_name = 'repertoire/variation_modify_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opening'] = Opening.objects.get(pk=self.kwargs['opening_name'])
        context['variation'] = Variation.objects.get(pk=self.kwargs['pk'])
        return context


# -- APP Views -- #
class ReviewVariation(View):
    template_name = 'repertoire/review.html'

    def get_context_data(self):
        return {
            'opening': self.opening,
            'variation': self.variation,
            'board': mark_safe(self.reviewer.board),
            'all_moves': self.reviewer.possible_moves,
            'turn': self.request.session['turn']
        }

    def dispatch(self, request, *args, **kwargs):
        self.opening = Opening.objects.get(pk=self.kwargs['opening_name'])
        self.variation = Variation.objects.get(pk=self.kwargs['pk'])

        # -- Initialize Reviewer -- #
        self.reviewer = ChessReviewer(
            self.variation.pgn_file.path,
            self.variation.opening.color,
            run_moves=self.request.session['moves']
        )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # -- Undo Move -- #
        if self.request.POST.get('undo', None):
            self.reviewer.undo_move()
            self.request.session['moves'].pop()
            self.request.session['turn'] = not self.request.session['turn']
            context = self.get_context_data()
        # -- Restart Reviewing -- #
        elif self.request.POST.get('restart', None):
            self.request.session['moves'] = []
            self.request.session['turn'] = False
            self.reviewer.restart()
            context = self.get_context_data()
        # -- Execute Move -- #
        else:
            for move in self.reviewer.possible_moves:
                if self.request.POST.get(move, None):
                    self.reviewer.next_move(move)
                    self.request.session['moves'].append(move)
                    self.request.session['turn'] = not self.request.session['turn']
                    context = self.get_context_data()
        return render(self.request, self.template_name, context)


class PracticeVariation(View):
    template_name = 'repertoire/practice.html'

    def get_context_data(self, correct=-1):
        return {
            'opening': self.opening,
            'variation': self.variation,
            'board': mark_safe(self.practice.board),
            'correct': correct
        }
    
    def dispatch(self, request, *args, **kwargs):
        self.opening = Opening.objects.get(pk=self.kwargs['opening_name'])
        self.variation = Variation.objects.get(pk=self.kwargs['pk'])

        # -- Initialize Reviewer -- #
        self.practice = ChessPractice(
            self.variation.pgn_file.path,
            self.variation.opening.color,
        )
        self.request.session['moves'] = self.practice.run_visited_moves(
            self.request.session['moves']
        )
        
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # -- Check if Player entered a Move -- #
        move = self.request.POST.get('move', None)
        if move != '':
            # -- Move was entered -- #
            if self.practice.check_if_correct(move):
                correct = True
                opp_move = self.practice.player_move(move)
                self.request.session['moves'] += [move, opp_move]
            else:
                correct = False
        else:
            # -- Practice Again the Game -- #
            self.request.session['moves'] = self.practice.restart()
            correct = -1
        context = self.get_context_data(correct=correct)
        return render(self.request, self.template_name, context)