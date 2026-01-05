from django.views.generic import (CreateView, DetailView, ListView, UpdateView, TemplateView)
from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.http import JsonResponse
import json

from chess_repertoire.apps.game import (
    ChessReviewer, ChessPractice, get_current_turn, read_pgn_file, update_pgn_file
)
from chess_repertoire.apps.game.statistics import PracticeStatistics
from .constants import MAX_OPENING_PER_PAGE, MAX_VARIATION_PER_PAGE
from .models import Opening, Variation
from .forms import OpeningForm, VariationForm
from .filters import OpeningFilter, VariationFilter
from .mixins import PracticeAjaxMixin

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
        context['opening'] = Opening.objects.get(slug=self.kwargs['slug'])
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
            self.request.session['turn'] = get_current_turn(self.request.session['moves'])
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        opening = Opening.objects.get(slug=self.kwargs['slug'])
        variations = opening.variation_set.all()
        return variations
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opening'] = Opening.objects.get(slug=self.kwargs['slug'])
        context['filter'] = VariationFilter(self.request.GET, queryset=self.get_queryset())
        # -- Pagination with Filtering -- #
        paginator = Paginator(context['filter'].qs, OpeningVariations.paginate_by)
        page_number = self.request.GET.get('page')
        variations = paginator.get_page(page_number)
        context['variations'] = variations
        return context


class NewVariation(CreateView):
    model = Variation
    form_class = VariationForm
    template_name = 'repertoire/variation_new_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opening'] = Opening.objects.get(slug=self.kwargs['slug'])
        return context

    def form_valid(self, form):
        form.instance.opening = Opening.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)


class ModifyVariation(UpdateView):
    model = Variation
    form_class = VariationForm
    template_name = 'repertoire/variation_modify_form.html'

    def form_valid(self, form):
        variation = Variation.objects.get(slug=self.kwargs['slug'])
        head, moves = read_pgn_file(variation.pgn_file.url)
        pgn_content = self.request.POST.get('pgn_content', None).replace('\r', '')
        if pgn_content:
            if moves != pgn_content:
                full_pgn_content = head + '\n\n' + pgn_content
                update_pgn_file(variation.pgn_file.url, full_pgn_content)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opening'] = Opening.objects.get(name=self.kwargs['opn'])
        context['variation'] = Variation.objects.get(slug=self.kwargs['slug'])
        _, context['pgn_content'] = read_pgn_file(context['variation'].pgn_file.url)
        return context


# -- APP Views -- #
class ReviewVariation(View):
    template_name = 'repertoire/review.html'

    def dispatch(self, request, *args, **kwargs):
        self.opening = Opening.objects.get(name=self.kwargs['opn'])
        self.variation = Variation.objects.get(slug=self.kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'opening': self.opening,
            'variation': self.variation,
        }
        return render(self.request, self.template_name, context)


class PracticeVariation(View):
    template_name = 'repertoire/practice.html'

    def get_context_data(self, correct='other'):
        correct = correct if self.practice.possible_moves else 'finished'
        return {
            'opening': self.opening,
            'variation': self.variation,
            'board': mark_safe(self.practice.board),
            'correct': correct,
            'nag': self.practice.nag,
            'is_checkmate': self.practice.is_checkmate,
            'start_flag': len(self.request.session['moves']) == 0,
        }
    
    def dispatch(self, request, *args, **kwargs):
        self.opening = Opening.objects.get(name=self.kwargs['opn'])
        self.variation = Variation.objects.get(slug=self.kwargs['slug'])

        # -- Initialize Practice -- #
        self.practice = ChessPractice(
            self.variation.pgn_file.path,
            self.variation.opening.color,
        )
        self.request.session['moves'] = self.practice.run_visited_moves(
            self.request.session['moves']
        )

        # Initialize statistics if needed
        stats = PracticeStatistics.get_stats(self.request.session)
        if not stats or stats.get('variation_slug') != self.kwargs['slug']:
            PracticeStatistics.initialize_stats(
                self.request.session,
                self.opening.name,
                self.variation.slug
            )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(self.request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # -- Check if Player entered a Move -- #
        move = self.request.POST.get('move', '')
        if move != '':
            # -- Move was entered -- #
            if self.practice.check_if_correct(move):
                correct = 'correct'
                try:
                    opp_move = self.practice.player_move(move)
                    self.request.session['moves'] += [move, opp_move]
                except Exception:
                    self.request.session['moves'] += [move]
            else:
                correct = 'incorrect'
        # -- Show Hints of the Possible Moves -- #
        elif self.request.POST.get('hint', None):
            self.practice.show_hints
            correct = 'hint'
        # -- Practice Again the Game -- #
        else:
            self.request.session['moves'] = self.practice.restart()
            correct = 'other'
        context = self.get_context_data(correct=correct)
        return render(self.request, self.template_name, context)


# -- AJAX Views for Drag-and-Drop Practice Mode -- #
class PracticeValidateMove(PracticeAjaxMixin, View):
    """AJAX endpoint to validate player's move and get opponent's response"""

    def post(self, request, *args, **kwargs):
        # Parse request data
        data = json.loads(request.body)
        move = data.get('move', '')

        # Get practice context (opening, variation, practice instance)
        context = self.get_practice_context()
        practice = context['practice']

        # Validate the move
        if practice.check_if_correct(move):
            # Record correct move
            PracticeStatistics.record_move(request.session, move, correct=True)

            try:
                # Execute player move and get opponent's response
                opp_move = practice.player_move(move)
                request.session['moves'] += [move, opp_move]

                return JsonResponse({
                    'correct': True,
                    'opponent_move': opp_move,
                    'fen': practice.state.board().fen(),
                    'is_checkmate': practice.is_checkmate,
                    'nag': practice.nag
                })
            except Exception:
                # No opponent move available (practice finished)
                PracticeStatistics.mark_completed(request.session)
                request.session['moves'] += [move]
                return JsonResponse({
                    'correct': True,
                    'opponent_move': None,
                    'fen': practice.state.board().fen(),
                    'is_checkmate': practice.is_checkmate,
                    'nag': practice.nag
                })
        else:
            # Record incorrect move
            PracticeStatistics.record_move(request.session, move, correct=False)

            # Move is incorrect
            return JsonResponse({
                'correct': False,
                'opponent_move': None,
                'fen': practice.state.board().fen(),
                'is_checkmate': practice.is_checkmate,
                'nag': practice.nag
            })


class PracticeGetPosition(PracticeAjaxMixin, View):
    """AJAX endpoint to get current board position"""

    def get(self, request, *args, **kwargs):
        # Get practice context (opening, variation, practice instance)
        context = self.get_practice_context()
        practice = context['practice']
        opening = context['opening']

        # Determine if it's player's turn
        is_player_turn = self.get_player_turn_status(opening)

        # Check if practice is finished
        finished = not bool(practice.possible_moves)

        return JsonResponse({
            'fen': practice.state.board().fen(),
            'is_player_turn': is_player_turn,
            'finished': finished,
            'is_checkmate': practice.is_checkmate,
            'nag': practice.nag
        })


class PracticeGetHints(PracticeAjaxMixin, View):
    """AJAX endpoint to get legal moves for hints"""

    def post(self, request, *args, **kwargs):
        # Get practice context (opening, variation, practice instance)
        context = self.get_practice_context()
        practice = context['practice']

        # Get legal moves with UCI format (from/to squares)
        legal_moves = []
        for i in range(len(practice.state.variations)):
            variation_move = practice.state.variations[i].move
            legal_moves.append({
                'from': variation_move.from_square,
                'to': variation_move.to_square,
                'san': practice.state.board().san(variation_move)
            })

        # Record hint usage
        PracticeStatistics.record_hint(request.session)

        return JsonResponse({
            'legal_moves': legal_moves,
            'nag': practice.nag
        })


class PracticeRestart(PracticeAjaxMixin, View):
    """AJAX endpoint to restart practice"""

    def post(self, request, *args, **kwargs):
        # Get practice context (opening, variation, practice instance)
        context = self.get_practice_context()
        practice = context['practice']
        opening = context['opening']

        # Restart and get initial moves
        request.session['moves'] = practice.restart()

        # Determine if it's player's turn
        is_player_turn = self.get_player_turn_status(opening)

        return JsonResponse({
            'fen': practice.state.board().fen(),
            'is_player_turn': is_player_turn,
            'nag': practice.nag
        })


class PracticeGetStatistics(View):
    """AJAX endpoint to get current statistics"""

    def get(self, request, *args, **kwargs):
        try:
            stats = PracticeStatistics.get_stats(request.session)

            if not stats:
                return JsonResponse({'error': 'No statistics'}, status=404)

            if (stats.get('opening_name') != kwargs['opn'] or
                stats.get('variation_slug') != kwargs['slug']):
                return JsonResponse({'error': 'Stats mismatch'}, status=400)

            summary = PracticeStatistics.get_stats_summary(stats)

            return JsonResponse({
                'correct_moves': stats['correct_moves'],
                'incorrect_moves': stats['incorrect_moves'],
                'hints_used': stats['hints_used'],
                'accuracy': summary['accuracy'],
                'total_attempts': summary['total_attempts'],
                'completed': stats['completed']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# -- AJAX Views for Review Mode -- #
class ReviewExecuteMove(View):
    """AJAX endpoint to execute a move in review mode"""

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        move = data.get('move', '')

        opening = Opening.objects.get(name=kwargs['opn'])
        variation = Variation.objects.get(slug=kwargs['slug'])

        # Initialize moves list if not present
        if 'moves' not in request.session or request.session['moves'] is None:
            request.session['moves'] = []

        reviewer = ChessReviewer(variation.pgn_file.path, opening.color)
        # Note: run_visited_moves returns None, it just updates the reviewer state
        reviewer.run_visited_moves(request.session['moves'])

        # Validate and execute move
        if move in reviewer.possible_moves:
            reviewer.next_move(move)
            request.session['moves'].append(move)

        request.session.modified = True

        return JsonResponse({
            'fen': reviewer.state.board().fen(),
            'possible_moves': reviewer.possible_moves,
            'nag': reviewer.nag,
            'is_checkmate': reviewer.is_checkmate,
            'finished': not bool(reviewer.possible_moves)
        })


class ReviewUndoMove(View):
    """AJAX endpoint to undo the last move"""

    def post(self, request, *args, **kwargs):
        opening = Opening.objects.get(name=kwargs['opn'])
        variation = Variation.objects.get(slug=kwargs['slug'])

        # Initialize moves list if not present
        if 'moves' not in request.session or request.session['moves'] is None:
            request.session['moves'] = []

        # Pop last move if exists
        if request.session['moves']:
            request.session['moves'].pop()

        reviewer = ChessReviewer(variation.pgn_file.path, opening.color)
        # Note: run_visited_moves returns None, it just updates the reviewer state
        reviewer.run_visited_moves(request.session['moves'])

        request.session.modified = True

        return JsonResponse({
            'fen': reviewer.state.board().fen(),
            'possible_moves': reviewer.possible_moves,
            'nag': reviewer.nag,
            'is_checkmate': reviewer.is_checkmate,
            'moves_count': len(request.session['moves'])
        })


class ReviewRestart(View):
    """AJAX endpoint to restart review from beginning"""

    def post(self, request, *args, **kwargs):
        opening = Opening.objects.get(name=kwargs['opn'])
        variation = Variation.objects.get(slug=kwargs['slug'])

        reviewer = ChessReviewer(variation.pgn_file.path, opening.color)
        restarted_moves = reviewer.restart()

        # Ensure we have a valid list
        request.session['moves'] = restarted_moves if restarted_moves is not None else []
        request.session.modified = True

        return JsonResponse({
            'fen': reviewer.state.board().fen(),
            'possible_moves': reviewer.possible_moves,
            'nag': reviewer.nag,
            'is_checkmate': reviewer.is_checkmate,
            'orientation': 'white' if opening.color == 0 else 'black'
        })


class ReviewGetPosition(View):
    """AJAX endpoint to get current board state"""

    def get(self, request, *args, **kwargs):
        opening = Opening.objects.get(name=kwargs['opn'])
        variation = Variation.objects.get(slug=kwargs['slug'])

        # Initialize moves list if not present
        if 'moves' not in request.session or request.session['moves'] is None:
            request.session['moves'] = []

        reviewer = ChessReviewer(variation.pgn_file.path, opening.color)
        # Note: run_visited_moves returns None, it just updates the reviewer state
        reviewer.run_visited_moves(request.session['moves'])

        request.session.modified = True

        return JsonResponse({
            'fen': reviewer.state.board().fen(),
            'possible_moves': reviewer.possible_moves,
            'nag': reviewer.nag,
            'is_checkmate': reviewer.is_checkmate,
            'start_flag': len(request.session['moves']) == 0,
            'orientation': 'white' if opening.color == 0 else 'black'
        })