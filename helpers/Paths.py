import os

HOME_PATH = os.getenv('HOMEPATH')
RESULT_PATH = os.path.join('C:\\', HOME_PATH, 'Desktop', 'result')
DATABASE_PATH = os.path.join('C:\\', HOME_PATH, 'Documents', "Actions.db")
RESULT_PATH = os.path.normpath(RESULT_PATH)
