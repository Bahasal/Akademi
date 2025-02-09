import os

class Config:
    """
    Uygulama için temel yapılandırma ayarları.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'bu-cok-gizli-bir-anahtar')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///veritabani.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('DEBUG', True)
