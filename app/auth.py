from authx import AuthX, AuthXConfig

from app.config import config as app_config


config = AuthXConfig()
config.JWT_ALGORITHM = 'HS256'
config.JWT_ACCESS_COOKIE_NAME = 'magic_app_cookie'
config.JWT_SECRET_KEY = app_config.JWT_SECRET_KEY
config.JWT_TOKEN_LOCATION = ['cookie']


auth = AuthX(config=config)
