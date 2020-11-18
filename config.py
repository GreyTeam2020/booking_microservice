from os.path import abspath, dirname

_cwd = dirname(abspath(__file__))


class BaseConfiguration(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "flask-session-insecure-secret-key"
    HASH_ROUNDS = 100000


class DebugConfiguration(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = "DEBUG_flask-session-insecure-secret-key"
    HASH_ROUNDS = 100000


class TestConfiguration(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = "DEBUG_flask-session-insecure-secret-key"
    HASH_ROUNDS = 100000
