from sqlalchemy import create_engine, and_, QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from util.encryptor import encrypt, decrypt
from util.config import get_config

BaseClass = declarative_base()

def get_database_config():
    host = get_config("DATABASE_HOST", "localhost")
    port = get_config("DATABASE_PORT", "3306")
    user = get_config("DATABASE_USERNAME", "root")
    password = get_config("DATABASE_PASSWORD", "root")
    database = get_config("DATABASE_NAME", "tongla-hub")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

class Base(BaseClass):
    __abstract__ = True
    __encrypted_field__ = []

    session = None
    query = None

    def __init__(self):
        self.create_new_session()
        super().__init__()

    def close_connection(self):
        if self.session is not None:
            self.session.close()
            self.session = None
            self.query = None

    def create_new_session(self):
        if self.session is not None:
            return

        engine = create_engine(
            get_database_config(),
            echo=True,
            poolclass=QueuePool,
            pool_size=50,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800
        )
        session_maker = sessionmaker(bind=engine)
        self.session = session_maker()
        self.query = self.session.query(self.__class__)

    def create(self, values: dict):
        try:
            self.create_new_session()

            for key, value in values.items():
                setattr(self, key, value)

            for field in self.__encrypted_field__:
                setattr(self, field, encrypt(getattr(self, field)))

            self.session.add(self)
            self.session.commit()
            self.session.refresh(self)

            for field in self.__encrypted_field__:
                decrypted_value = decrypt(getattr(self, field))
                setattr(self, field, decrypted_value)

            self.close_connection()
            return self
        except Exception as e:
            self.session.rollback()
            raise e

    def update(self, values: dict):
        try:
            self.create_new_session()

            for key, value in values.items():
                setattr(self, key, value)

            for field in self.__encrypted_field__:
                setattr(self, field, encrypt(getattr(self, field)))

            self.session.merge(self)
            self.session.commit()

            for field in self.__encrypted_field__:
                decrypted_value = decrypt(getattr(self, field))
                setattr(self, field, decrypted_value)

            self.close_connection()
            return self
        except Exception as e:
            self.session.rollback()
            raise e


    def get_by_id(self, id):
        self.create_new_session()
        record = self.query.get(id)

        for field in self.__encrypted_field__:
            decrypted_value = decrypt(getattr(record, field))
            setattr(record, field, decrypted_value)

        self.close_connection()
        return record

    def filter(self, filters, limit=1000):
        self.create_new_session()
        filter_query = []
        for field, condition, value in filters:
            if condition == "ilike":
                filter_query.append(getattr(self.__class__, field).ilike(f"%{value}%"))
            elif condition == "<=":
                filter_query.append(getattr(self.__class__, field) <= value)
            elif condition == ">=":
                filter_query.append(getattr(self.__class__, field) >= value)
            elif condition == "in":
                filter_query.append(getattr(self.__class__, field).in_(value))
            else:
                filter_query.append(getattr(self.__class__, field) == value)

        records = self.query.filter(and_(*filter_query)).limit(limit).all()
        result_list = []

        for record in records:
            for field in self.__encrypted_field__:
                decrypted_value = decrypt(getattr(record, field))
                setattr(record, field, decrypted_value)
            result_list.append(record)

        self.close_connection()
        return result_list

    def __del__(self):
        self.close_connection()

    def __enter__(self):
        return self
