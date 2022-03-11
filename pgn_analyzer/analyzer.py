import logging
import chess.engine as eng
import chess.pgn as pgn

from tqdm import tqdm

class PGNAnalyzer():
    def __init__(self, engine_cfg):
        logging.info('Building Engine...')
        self.engine = eng.SimpleEngine.popen_uci(engine_cfg.path)
        logging.info('Done')
        self.cfg = engine_cfg
    
    @staticmethod
    def read_pgn(pgn_path):
        with open(pgn_path, 'r') as file:
            state = pgn.read_game(file)
        return state

    def run_analysis(self, pgn_path):
        state = PGNAnalyzer.read_pgn(pgn_path)
        self.pbar = tqdm(total=100, desc=f'{pgn_path.stem}')
        self.analyze(state.next())
        self.pbar.close()
        return state

    def compute_score(self, state):
        info = self.engine.analyse(state.board(), eng.Limit(depth=self.cfg.depth))
        score = info['score'].white().score(
            mate_score=self.cfg.mate_score
        )/self.cfg.mate_score
        return score
    
    def get_variations(self, state):
        return [state.variations[x].move for x in range(len(state.variations))]

    def analyze(self, state):
        self.pbar.update(1)
        state.comment = str(self.compute_score(state))
        if state.variations:
            all_variations = [state.variation(move) for move in self.get_variations(state)]
            for variation in all_variations:
                self.analyze(variation)

    def save(self, state, save_filename):
        pgn_content = str(state)
        with open(save_filename, 'w') as file:
            file.write(pgn_content)
