from db.engine.engine import engine_init_local, engine_init_remote
from db.session.session import create_session_factory
from db.models.Job import Job
from sqlalchemy import or_


def remove_null_entries(logger, env="dev"):
    logger.info("Removing null entries from the database...")

    if env == "prod":
        logger.info("Using remote database")
        engine = engine_init_remote()
    else:
        logger.info("Using local database")
        engine = engine_init_local()

    SessionLocal = create_session_factory(engine)

    with SessionLocal() as session:
        deleted_count = (
            session.query(Job)
            .filter(
                or_(
                    Job.title.is_(None),
                    Job.work_type.is_(None),
                    Job.salary.is_(None),
                    Job.hours_per_week.is_(None),
                    Job.job_overview.is_(None),
                )
            )
            .delete(synchronize_session=False)
        )

        session.commit()
        logger.info(f"Removed {deleted_count} null entries successfully.")
