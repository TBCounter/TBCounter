import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    PG_USER = os.environ.get('PG_USER')
    PG_PASSWORD = os.environ.get('PG_PASSWORD')
    PG_URL = os.environ.get('PG_URL')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_URL}:5433/totalbattle"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
