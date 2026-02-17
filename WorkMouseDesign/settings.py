import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = str(Path(sys.executable).resolve().parent).replace('\\', '/') + "/bin"
else:
    # BASE_DIR = Path(__file__).resolve().parent
    BASE_DIR = str(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/')

ProjectDirectory = os.path.dirname(os.path.realpath(__file__))

SourceDataDir = BASE_DIR + '/resources/pet/'
