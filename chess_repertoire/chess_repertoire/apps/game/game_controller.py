import chess.pgn as pgn
import chess.svg as svg

from chess_repertoire.apps.repertoire.constants import CHESS_BOARD_SIZE

class ChessReviewer():
    def __init__(self, pgn_file, color, run_moves=[], size=CHESS_BOARD_SIZE):
        self.state = ChessReviewer.read_pgn_file(pgn_file)
        self.flipped = True if color else False
        self.run_visited_moves(run_moves)
        self.pgn_path = pgn_file
        self.size = size

    @staticmethod
    def read_pgn_file(pgn_file):
        with open(pgn_file) as file:
            return pgn.read_game(file)

    @property
    def board(self):
        return svg.board(
            board=self.state.board(), size=self.size, flipped=self.flipped, lastmove=self.state.move
        )
    
    @property
    def possible_moves(self):
        uci_moves = [self.state.variations[x].move for x in range(len(self.state.variations))]
        self.moves = []
        for move in uci_moves:
            self.moves.append(self.state.board().san(move))
        return self.moves

    def run_visited_moves(self, run_moves):
        for move in run_moves:
            self.next_move(move)
    
    def next_move(self, move):
        self.possible_moves
        index = self.moves.index(move)
        self.state = self.state.variations[index]
        
    def undo_move(self):
        self.state = self.state.parent

    def restart(self):
        self.state = ChessReviewer.read_pgn_file(self.pgn_path)

class ChessPractice(ChessReviewer):
    pass
    