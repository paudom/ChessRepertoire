from .constants import REPERTOIRE_ROOT

# -- Util Functions -- #
def read_pgn_file(pgn_path):
    with open(REPERTOIRE_ROOT + pgn_path, 'r') as file:
        full_lines = file.read().split(']')
        head = ''.join([text + ']' for text in full_lines[:-1]])
        moves = full_lines[-1].strip()
    return head, moves

def update_pgn_file(pgn_path, pgn_content):
    with open(REPERTOIRE_ROOT + pgn_path, 'w') as file:
        file.write(pgn_content)