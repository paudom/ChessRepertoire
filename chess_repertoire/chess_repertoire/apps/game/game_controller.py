import chess.pgn as pgn
import chess.svg as svg
import random

from chess_repertoire.apps.repertoire.constants import CHESS_BOARD_SIZE


class ChessBase():
    def __init__(self, pgn_file, color, size=CHESS_BOARD_SIZE):
        self.state = ChessBase.read_pgn_file(pgn_file)
        self.color = True if color else False
        self.pgn_path = pgn_file
        self.size = size

    @staticmethod
    def read_pgn_file(pgn_file):
        with open(pgn_file) as file:
            return pgn.read_game(file)

    @property
    def board(self):
        return svg.board(
            board=self.state.board(), size=self.size, flipped=self.color, lastmove=self.state.move
        )
    
    @property
    def possible_moves(self):
        uci_moves = [self.state.variations[x].move for x in range(len(self.state.variations))]
        self.moves = []
        for move in uci_moves:
            self.moves.append(self.state.board().san(move))
        return self.moves

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
        if self.color and not run_moves:
            opp_move = self.opponent_move()
            run_moves.append(opp_move)
        for move in run_moves:
            self.next_move(move)
        return run_moves
        
    def check_if_correct(self, move):
        return True if move in self.possible_moves else False
    
    def opponent_move(self):
        moves = self.possible_moves
        selected_move = random.choice(moves)
        return selected_move
    
    def player_move(self, move):
        self.next_move(move)
        opp_move = self.opponent_move()
        self.next_move(opp_move)
        return opp_move
    
    def restart(self):
        self.state = ChessBase.read_pgn_file(self.pgn_path)
        moves = self.run_visited_moves([])
        return moves
        