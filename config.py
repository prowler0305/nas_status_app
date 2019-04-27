import os
import datetime

container_status_app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = os.environ.get('USCC_SECRET_KEY') or 'you-will-never-guess'
    JWT_SECRET_KEY = os.environ.get('USCC_JWT_KEY') or 'super-secret'
    JWT_HEADER_TYPE = 'JWT'
    PROPAGATE_EXCEPTIONS = True
    THREADED = True
    # INFO: temporary code while login app is being used here.
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    PREFERRED_URL_SCHEME = 'https'
    UPLOAD_FOLDER = os.path.join('container_status_app', os.environ.get('upload_dir'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # INFO: 16MB upload size maximum
    USCC_MAIL_SERVER_URL = "Corpmta.uscc.com"
    USCC_MAIL_SERVER_PORT = 25


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    PORT = 5000 if os.environ.get("PORT") is None else int(os.environ.get("PORT"))
    HOST = os.environ.get('HOST') or 'localhost'
    PREFERRED_URL_SCHEME = 'http'
    USCC_MAIL_SERVER_URL = "localhost"
    USCC_MAIL_SERVER_PORT = 1025
    if os.environ.get('access_token_expiration') is not None:
        JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=int(os.environ.get('access_token_expiration')))
    if os.environ.get('refresh_token_expiration') is not None:
        JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(seconds=int(os.environ.get('refresh_token_expiration')))


class QaConfig(BaseConfig):
    DEBUG = True
    PORT = 8080 if os.environ.get("PORT") is None else int(os.environ.get('PORT'))
    HOST = os.environ.get('HOST') or '0.0.0.0'
    if os.environ.get('access_token_expiration') is not None:
        JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=int(os.environ.get('access_token_expiration')))
    if os.environ.get('refresh_token_expiration') is not None:
        JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(seconds=int(os.environ.get('refresh_token_expiration')))


class ProductionConfig(BaseConfig):
    DEBUG = False
    PORT = 8080 if os.environ.get("PORT") is None else int(os.environ.get('PORT'))
    HOST = os.environ.get('HOST') or '0.0.0.0'
    if os.environ.get('access_token_expiration') is not None:
        JWT_ACCESS_EXP = datetime.timedelta(seconds=int(os.environ.get('access_token_expiration')))
    if os.environ.get('refresh_token_expiration') is not None:
        JWT_REFRESH_EXP = datetime.timedelta(seconds=int(os.environ.get('refresh_token_expiration')))
