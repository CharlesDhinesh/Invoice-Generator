from dotenv import load_dotenv
import os
import json

load_dotenv()  # loads .env

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS") == "True"
    SQLALCHEMY_ENGINE_OPTIONS = json.loads(os.getenv("SQLALCHEMY_ENGINE_OPTIONS"))


    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "charlesdhinesh01@gmail.com"
    MAIL_PASSWORD = "qndnzrlttmvnakdr"
