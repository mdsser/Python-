import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, 'config', '.env'), override=True)

class Config:
    DB_TYPE = os.getenv('DB_TYPE', 'mysql')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'autoops')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'autoops123')
    DB_NAME = os.getenv('DB_NAME', 'autoops')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change_this_secret')
    # 邮件
    MAIL_HOST = os.getenv('MAIL_HOST', '')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 25))
    MAIL_USER = os.getenv('MAIL_USER', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_RECEIVERS = os.getenv('MAIL_RECEIVERS', '').split(',')
