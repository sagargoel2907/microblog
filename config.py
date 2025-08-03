from os import getenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = getenv('SECRET_KEY') or 'secret_key'
    SQLALCHEMY_DATABASE_URI = getenv(
        'SQLALCHEMY_DATABASE_URI') or f'sqlite:///{os.path.join(basedir, 'app.db')}'
    MAIL_SERVER = getenv('MAIL_SERVER')
    MAIL_PORT = int(getenv('MAIL_PORT') or 25)
    MAIL_USE_TLS = getenv('MAIL_USE_TLS') is not None
    MAIL_USERNAME = getenv('MAIL_USERNAME')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD')
    ADMINS = ['sagargoel2907@gmail.com']
