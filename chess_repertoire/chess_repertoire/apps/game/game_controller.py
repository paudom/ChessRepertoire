import chess.pgn as pgn
import chess.svg as svg
import random

from chess_repertoire.apps.repertoire.constants import CHESS_BOARD_SIZE

def read_pgn_file(pgn_file):
    with open(pgn_file) as file:
        return pgn.read_game(file)

class ChessReviewer():
    def __init__(self, pgn_file, color, run_moves=[], size=CHESS_BOARD_SIZE):
        self.state = read_pgn_file(pgn_file)
        self.color = True if color else False
        self.run_visited_moves(run_moves)
        self.pgn_path = pgn_file
        self.size = size

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
    def __init__(self, *args, **kwargs):
        self.first_move = None
        super().__init__(*args, **kwargs)

    def run_visited_moves(self, run_moves):
        if self.color and not run_moves:
            opp_move = self.opponent_move()
            run_moves.append(opp_move)
            self.first_move = opp_move
        super().run_visited_moves(run_moves)

    def next_move(self, move):
        print(self.moves)
        super().next_move(move)
        print(self.moves)
        opp_move = self.opponent_move()
        super().next_move(opp_move)
        print(self.moves)
        return opp_move

    def opponent_move(self):
        moves = self.possible_moves
        selected_move = random.choice(moves)
        super().next_move(selected_move)
        return selected_move