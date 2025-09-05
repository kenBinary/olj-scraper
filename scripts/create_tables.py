from db.engine.engine import engine_init
from db.models.Base import Base
# Need to import all models here because otherwise they won't be registered in Base
from db.models.Job import Job


def main():
    engine = engine_init()
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
