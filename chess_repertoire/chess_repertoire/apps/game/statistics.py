from datetime import datetime

class PracticeStatistics:
    """
    Static methods for managing practice session statistics in Django sessions.

    All methods operate on request.session['practice_stats'] dictionary.
    Statistics are tracked per variation and reset when switching variations
    or navigating away from practice mode.
    """

    SESSION_KEY = 'practice_stats'

    @staticmethod
    def initialize_stats(session, opening_name, variation_slug):
        """Initialize fresh statistics for a new practice session."""
        now = datetime.now().isoformat()

        session[PracticeStatistics.SESSION_KEY] = {
            'variation_slug': variation_slug,
            'opening_name': opening_name,
            'start_time': now,
            'last_activity': now,
            'correct_moves': 0,
            'incorrect_moves': 0,
            'hints_used': 0,
            'restarts': 0,
            'completed': False,
            'move_history': []
        }
        session.modified = True

    @staticmethod
    def get_stats(session):
        """Retrieve current statistics from session."""
        return session.get(PracticeStatistics.SESSION_KEY)

    @staticmethod
    def record_move(session, move, correct):
        """Record a move attempt (correct or incorrect)."""
        stats = PracticeStatistics.get_stats(session)
        if not stats:
            return

        # Update counters
        if correct:
            stats['correct_moves'] += 1
        else:
            stats['incorrect_moves'] += 1

        # Update activity timestamp
        stats['last_activity'] = datetime.now().isoformat()

        # Record in move history
        stats['move_history'].append({
            'move': move,
            'correct': correct,
            'timestamp': stats['last_activity']
        })

        session[PracticeStatistics.SESSION_KEY] = stats
        session.modified = True

    @staticmethod
    def record_hint(session):
        """Record hint usage."""
        stats = PracticeStatistics.get_stats(session)
        if not stats:
            return

        stats['hints_used'] += 1
        stats['last_activity'] = datetime.now().isoformat()

        session[PracticeStatistics.SESSION_KEY] = stats
        session.modified = True

    @staticmethod
    def mark_completed(session):
        """Mark practice session as completed."""
        stats = PracticeStatistics.get_stats(session)
        if not stats:
            return

        stats['completed'] = True
        stats['last_activity'] = datetime.now().isoformat()

        session[PracticeStatistics.SESSION_KEY] = stats
        session.modified = True

    @staticmethod
    def calculate_accuracy(stats):
        """Calculate accuracy percentage."""
        if not stats:
            return 0.0

        total_moves = stats['correct_moves'] + stats['incorrect_moves']
        if total_moves == 0:
            return 0.0

        return (stats['correct_moves'] / total_moves) * 100

    @staticmethod
    def get_duration_seconds(stats):
        """Calculate session duration in seconds."""
        if not stats:
            return 0

        try:
            start = datetime.fromisoformat(stats['start_time'])
            end = datetime.fromisoformat(stats['last_activity'])
            return int((end - start).total_seconds())
        except (ValueError, KeyError):
            return 0

    @staticmethod
    def format_duration(seconds):
        """Format duration as human-readable string."""
        if seconds < 60:
            return f"{seconds}s"

        minutes = seconds // 60
        remaining_seconds = seconds % 60

        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"

        hours = minutes // 60
        remaining_minutes = minutes % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds}s"

    @staticmethod
    def get_stats_summary(stats):
        """Get formatted summary for display."""
        if not stats:
            return {
                'accuracy': 0.0,
                'duration': '0s',
                'total_attempts': 0
            }

        accuracy = PracticeStatistics.calculate_accuracy(stats)
        duration_seconds = PracticeStatistics.get_duration_seconds(stats)
        duration = PracticeStatistics.format_duration(duration_seconds)
        total_attempts = stats['correct_moves'] + stats['incorrect_moves']

        return {
            'accuracy': accuracy,
            'duration': duration,
            'total_attempts': total_attempts
        }
