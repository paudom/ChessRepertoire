from chess_repertoire.apps.repertoire.constants import REPERTOIRE_ROOT
import chess.pgn as pgn

# -- Constants -- #
NAG_TO_EXPRESSION = {
    0: '',
    pgn.NAG_GOOD_MOVE: '!',
    pgn.NAG_BRILLIANT_MOVE: '!!',
    pgn.NAG_SPECULATIVE_MOVE: '!?',
    pgn.NAG_DUBIOUS_MOVE: '?!',
    pgn.NAG_MISTAKE: '?',
    pgn.NAG_BLUNDER: '??',
}

# -- Util Functions -- #
def get_current_turn(list_of_moves):
    return False if len(list_of_moves) % 2 == 0 else True

def get_current_color(list_of_moves):
    return 1 if get_current_turn(list_of_moves) else 0

def read_pgn_file(pgn_path):
    with open(REPERTOIRE_ROOT + pgn_path, 'r') as file:
        full_lines = file.read().split(']')
        head = ''.join([text + ']' for text in full_lines[:-1]])
        moves = full_lines[-1].strip()
    return head, moves

def update_pgn_file(pgn_path, pgn_content):
    with open(REPERTOIRE_ROOT + pgn_path, 'w') as file:
        file.write(pgn_content)