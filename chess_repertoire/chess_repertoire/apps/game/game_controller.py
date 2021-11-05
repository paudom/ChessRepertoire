import chess.pgn as pgn
import chess.svg as svg
import random

from chess_repertoire.apps.repertoire.constants import CHESS_BOARD_SIZE

from .utils import get_current_color

class ChessBase():
    def __init__(self, pgn_file, color, size=CHESS_BOARD_SIZE):
        self.state = ChessBase.read_pgn_file(pgn_file)
        self.color = True if color else False
        self.pgn_path = pgn_file
        self.size = size
        self.arrows = []

    @staticmethod
    def read_pgn_file(pgn_file):
        with open(pgn_file) as file:
            return pgn.read_game(file)

    @property
    def board(self):
        return svg.board(
            board=self.state.board(),
            size=self.size,
            arrows=self.arrows,
            flipped=self.color,
            lastmove=self.state.move
        )
    
    @property
    def possible_moves(self):
        uci_moves = [self.state.variations[x].move for x in range(len(self.state.variations))]
        self.moves = []
        for move in uci_moves:
            self.moves.append(self.state.board().san(move))
        return self.moves
    
    @property
    def show_hints(self):
        uci_moves = [self.state.variations[x].move for x in range(len(self.state.variations))]
        for move in uci_moves:
            self.arrows.append(svg.Arrow(
                move.from_square, move.to_square, color='blue'
            ))

    def next_move(self, move):
        self.possible_moves
        index = self.moves.index(move)
        self.state = self.state.variations[index]

    def run_visited_moves(self, run_moves):
        raise NotImplementedError('Yout are using the Base class. Use ChessReviewer or ChessPractice')

    def restart(self):
        raise NotImplementedError('Yout are using the Base class. Use ChessReviewer or ChessPractice')

class ChessReviewer(ChessBase):
    """Allows Reviewing a certain Variation"""

    def run_visited_moves(self, run_moves):
        for move in run_moves:
            self.next_move(move)
        
    def undo_move(self):
        self.state = self.state.parent

    def restart(self):
        self.state = ChessBase.read_pgn_file(self.pgn_path)

class ChessPractice(ChessBase):

    def run_visited_moves(self, run_moves):
        for move in run_moves:
            self.next_move(move)
        if self.color != get_current_color(run_moves):
            opp_move = self.opponent_move()
            if opp_move:
                self.next_move(opp_move)
                run_moves.append(opp_move)
        return run_moves
        
    def check_if_correct(self, move):
        return True if move in self.possible_moves else False
    
    def opponent_move(self):
        moves = self.possible_moves
        return random.choice(moves) if moves else None
    
    def player_move(self, move):
        self.next_move(move)
        opp_move = self.opponent_move()
        self.next_move(opp_move)
        return opp_move
    
    def restart(self):
        self.state = ChessBase.read_pgn_file(self.pgn_path)
        moves = self.run_visited_moves([])
        return moves
        