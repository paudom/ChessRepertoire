from django.http import JsonResponse

from chess_repertoire.apps.game import ChessPractice, get_current_color
from .models import Opening, Variation


class PracticeContextMixin:
    """
    Mixin providing common initialization logic for practice-related views.

    Handles opening/variation retrieval, ChessPractice initialization,
    and session state restoration.
    """

    def get_practice_context(self):
        """Retrieves opening, variation, and initializes ChessPractice instance."""
        opening = self.get_opening()
        variation = self.get_variation()
        practice = self.initialize_practice(opening, variation)
        self.restore_session_state(practice)
        return {
            'opening': opening,
            'variation': variation,
            'practice': practice
        }

    def get_opening(self):
        """Retrieves Opening instance from URL kwargs."""
        return Opening.objects.get(name=self.kwargs['opn'])

    def get_variation(self):
        """Retrieves Variation instance from URL kwargs."""
        return Variation.objects.get(slug=self.kwargs['slug'])

    def initialize_practice(self, opening, variation):
        """Creates ChessPractice instance."""
        return ChessPractice(
            variation.pgn_file.path,
            opening.color,
        )

    def restore_session_state(self, practice):
        """Restores practice state from session by running visited moves."""
        self.request.session['moves'] = practice.run_visited_moves(
            self.request.session.get('moves', [])
        )


class PracticeAjaxMixin(PracticeContextMixin):
    """
    Mixin specifically for AJAX practice endpoints.

    Provides standardized error handling and JSON response utilities.
    Extends PracticeContextMixin with AJAX-specific functionality.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to provide automatic error handling for AJAX views.

        Wraps view logic in try-except and returns JSON error responses
        for any exceptions that occur.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            return self.json_error_response(e)

    def json_error_response(self, error, status=500):
        """Returns standardized JSON error response."""
        return JsonResponse({'error': str(error)}, status=status)

    def get_player_turn_status(self, opening):
        """Calculates if it's player's turn based on session moves."""
        current_color = get_current_color(
            self.request.session.get('moves', [])
        )
        return opening.color == current_color
