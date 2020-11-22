import sys, os

os.environ["GOUOUTSAFE_TEST"] = "1"

from .tests.fixtures.client import *
from .tests.fixtures.clean_db import *
from .tests.test_utils import Utils

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
