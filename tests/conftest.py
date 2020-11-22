import sys, os

os.environ["GOUOUTSAFE_TEST"] = "1"

from fixtures.client import *
from fixtures.clean_db import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
