from sqlalchemy import create_engine, and_, QueuePool, or_, asc, desc
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

    def create(self, values=None):
        if values is None:
            values = {}

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

    def update(self, values=None):
        if values is None:
            values = {}

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

    def filter(self, filters=None, limit=1000, order_by=None):
        if filters is None:
            filters = []

        self.create_new_session()
        filter_query = []
        current_conditions = []
        or_conditions = []

        for condition in filters:
            if condition == "or":
                if current_conditions:
                    or_conditions.append(current_conditions)
                current_conditions = []
            elif condition == "and":
                continue
            else:
                field, condition_operator, value = condition
                if condition_operator == "ilike":
                    current_conditions.append(getattr(self.__class__, field).ilike(f"%{value}%"))
                elif condition_operator == "<=":
                    current_conditions.append(getattr(self.__class__, field) <= value)
                elif condition_operator == ">=":
                    current_conditions.append(getattr(self.__class__, field) >= value)
                elif condition_operator == "<":
                    current_conditions.append(getattr(self.__class__, field) < value)
                elif condition_operator == ">":
                    current_conditions.append(getattr(self.__class__, field) > value)
                elif condition_operator == "in":
                    current_conditions.append(getattr(self.__class__, field).in_(value))
                else:
                    current_conditions.append(getattr(self.__class__, field) == value)

        if current_conditions:
            or_conditions.append(current_conditions)

        if or_conditions:
            filter_query = or_(*[and_(*group) for group in or_conditions])
        else:
            filter_query = and_(*filter_query)

        if order_by:
            if isinstance(order_by, list):
                order_criteria = []
                for order_item in order_by:
                    if isinstance(order_item, tuple) and len(order_item) == 2:
                        field, direction = order_item
                        if direction.lower() == "desc":
                            order_criteria.append(desc(getattr(self.__class__, field)))
                        else:
                            order_criteria.append(asc(getattr(self.__class__, field)))
                    else:
                        order_criteria.append(asc(getattr(self.__class__, order_item)))
            else:
                order_criteria = [asc(getattr(self.__class__, order_by))]
        else:
            order_criteria = []

        query = self.query.filter(filter_query)
        if order_criteria:
            query = query.order_by(*order_criteria)

        records = query.limit(limit).all()
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
