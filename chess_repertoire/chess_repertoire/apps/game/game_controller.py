import chess.pgn as pgn
import chess.svg as svg

class ChessReviewer():
    def __init__(self, pgn_file, color, run_moves=[], size=500, turn=False):
        self.pgn_path = pgn_file
        self.state = ChessReviewer.read_pgn_file(pgn_file)
        self.size = size
        self.flipped = True if color else False
        self.turn = turn  # False is White, Black is True
        self.run_visited_moves(run_moves)

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
        uci_moves = [
            self.state.variations[x].move for x in range(len(self.state.variations))
        ]
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
        self.turn = not self.turn
        
    def undo_move(self):
        self.state = self.state.parent
        self.turn = not self.turn

    def restart(self):
        self.state = ChessReviewer.read_pgn_file(self.pgn_path)
        self.turn = False
