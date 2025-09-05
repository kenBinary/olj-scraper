from sqlalchemy.orm import sessionmaker


def create_session_factory(engine):
    return sessionmaker(autocommit=False, bind=engine)
