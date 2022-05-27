# PGN Analyzer
This tool computes the scores of each move given a PGN as comments.

## Requirements
In order to use it you will need the following:
- A version of Stockfish installed.
- A vitual environment with:
	- python-chess >= 1.6.0
	- hydra-core >= 1.1.0
	- tqdm

Then go to the file `pgn_analyzer.yaml` and add the path to the Stockfish under:
```yaml
engine:
	path: ???
```

## Usage
To use it you will need to call the script `pgn_analyzer.py`

```bash
python3 pgn_analyzer.py pgn_directory=${path where the pgns are located} output_dir=${location where to save the resulting pgns}
```