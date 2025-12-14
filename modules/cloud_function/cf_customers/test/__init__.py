import sys
import logging
from pathlib import Path


root_dir = Path(__file__).parent.parent.parent.parent.parent.resolve()

if root_dir not in map(Path.resolve, map(Path, sys.path)):
    logging.info(f"Adding {root_dir} to sys.path")
    sys.path.insert(0, str(root_dir))
else:
    logging.info("root_dir already in sys.path")