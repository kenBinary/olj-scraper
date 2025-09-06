from db.engine.engine import engine_init_local, engine_init_remote
from db.models.Base import Base
from utils.args_init import init_cli_args

# Need to import all models here because otherwise they won't be registered in Base
from db.models.Job import Job


def main():
    args = init_cli_args()
    print("Cleaning/Removing database tables...")
    if args.prod:
        print("Using remote database")
        engine = engine_init_remote()
        Base.metadata.drop_all(bind=engine)
    else:
        print("Using local database")
        engine = engine_init_local()
        Base.metadata.drop_all(bind=engine)
    print("Database tables removed successfully.")


if __name__ == "__main__":
    main()
