from models.Base import Base


def create_all_tables(engine):
    Base.metadata.create_all(bind=engine)
