import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Config:
    DATABASE_URL   = os.getenv('DATABASE_URL')
    DB_DATABASE    = os.getenv('DB_DATABASE')
    DB_DIALECT     = os.getenv('DB_DIALECT')
    DB_HOST        = os.getenv('DB_HOST')
    DB_PASSWORD    = os.getenv('DB_PASSWORD')
    DB_PORT        = os.getenv('DB_PORT')
    DB_SCHEMA      = os.getenv('DB_SCHEMA')
    DB_USER        = os.getenv('DB_USER')

    FRAMEWORK_NAME = os.getenv('FRAMEWORK_NAME')

    if DATABASE_URL is None:
        if DB_DIALECT and DB_DIALECT in 'postgresql mysql':
            DATABASE_URL = f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"    
        else:
            DATABASE_URL = f"sqlite:///{Path(__file__).parent}/app.db"
