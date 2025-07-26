
import os
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "daniel12345")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://neurotrack_user:7J0y8SJXhai46uGupUpLGsyaw9Z05dWw@dpg-d1rs2rbipnbc73cra9n0-a.oregon-postgres.render.com/neurotrack").replace("postgres://", "postgresql://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
