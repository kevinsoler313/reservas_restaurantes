import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, 'reservas.db')

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cambia_esta_clave_para_produccion')
