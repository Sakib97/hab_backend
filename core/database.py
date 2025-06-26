from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# they are coming from .env file
DB_USERNAME = config("db_username")
DB_PASSWORD = config("db_password")
DB_HOST = config("db_host")
DB_PORT = config("db_port")
DB_NAME = config("db_name")

# DB_USERNAME = config("db_username2")
# DB_PASSWORD = config("db_password2")
# DB_HOST = config("db_host2")
# DB_PORT = config("db_port2")
# DB_NAME = config("db_name2")

# postgresql://<username>:<password>@<host>:<port>/<database_name>
SQLALCHAMY_DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# print(SQLALCHAMY_DATABASE_URL)



engine = create_engine(SQLALCHAMY_DATABASE_URL) # create a SQLAlchemy "engine"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Each instance of the SessionLocal class will be a database session. 


Base = declarative_base() 

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()