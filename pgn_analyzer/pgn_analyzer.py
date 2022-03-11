import sys
import hydra
import logging

from pathlib import Path
from tqdm import tqdm
from analyzer import PGNAnalyzer

@hydra.main(config_path=Path(__file__).parent, config_name='pgn_analyzer')
def main(cfg):
    logging.info('Checking Directories')
    pgn_directory = Path(cfg.pgn_directory)
    assert pgn_directory.exists()
    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    logging.info('Done')

    logging.info('Building PGNConverter...')
    pgn_analyzer = PGNAnalyzer(cfg.engine)

    pbar = tqdm(sorted(list(pgn_directory.glob('**/*.pgn'))), desc='Analyzing PGNs')
    for pgn_path in pbar:
        state = pgn_analyzer.run_analysis(pgn_path)
        pgn_analyzer.save(state, save_filename=f'{output_dir / pgn_path.name}')
    pbar.close()
    logging.info('Done')
    sys.exit()
    
if __name__ == '__main__':
    main()