
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
            os.getenv('MYSQL_USER', 'ziheng'),
            os.getenv('MYSQL_PASS', ''),
            os.getenv('MYSQL_HOST', 'localhost'),
            os.getenv('MYSQL_DB', 'rayvita')
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
