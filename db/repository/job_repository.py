from db.models.Job import Job


def add_job(session, job: Job):
    session.add(job)


def add_jobs_bulk(session, jobs: list[Job]):
    session.add_all(jobs)


def get_all_jobs(session) -> list[Job]:
    return session.query(Job).all()


def get_job_by_job_id(session, job_id) -> Job | None:
    return session.query(Job).filter(Job.id == job_id).first()
