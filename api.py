from fastapi import Depends, FastAPI, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, OperationalError
from typing import Optional, List
from db.engine.engine import engine_init_local, engine_init_remote
from db.session.session import create_session_factory
from db.models.Job import Job
from services.logger.logger_config import Logger
import os
from dotenv import load_dotenv
import re
from sqlalchemy import func

app = FastAPI()

logger = Logger("main").get()
load_dotenv()
environment = os.getenv("API_ENV")
RETRY_COUNTS = int(os.getenv("API_FETCH_RETRY_COUNTS", 3))
if environment == "prod":
    logger.info("Running in production mode")
    engine = engine_init_remote()
else:
    logger.info("Running in development mode")
    engine = engine_init_local()

SessionLocal = create_session_factory(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def handle_db_connection_error(error, db: Session):
    error_str = str(error).lower()

    if (
        "stream not found" in error_str
        or "hrana" in error_str
        or "connection" in error_str
    ):
        logger.warning(f"Database connection error detected: {error}")

        try:
            db.close()

            global SessionLocal, engine
            if environment == "prod":
                logger.info("Reconnecting to remote database...")
                engine = engine_init_remote()
            else:
                logger.info("Reconnecting to local database...")
                engine = engine_init_local()

            SessionLocal = create_session_factory(engine)
            new_db = SessionLocal()
            logger.info("Database reconnection successful")
            return new_db

        except Exception as reconnect_error:
            logger.error(f"Failed to reconnect to database: {reconnect_error}")
            raise HTTPException(
                status_code=503,
                detail="Database service temporarily unavailable. Please try again in a moment.",
            )

    logger.error(f"Database error: {error}")
    raise HTTPException(
        status_code=500, detail="An error occurred while processing your request."
    )


@app.get("/api/jobs")
def read_jobs(
    db: Session = Depends(get_db),
    limit: int = Query(
        default=10, ge=1, le=100, description="Number of jobs to return (1-100)"
    ),
    offset: int = Query(default=0, ge=0, description="Number of jobs to skip"),
    page: Optional[int] = Query(
        default=None, ge=1, description="Page number (alternative to offset)"
    ),
    salary: Optional[str] = Query(default=None, description="Filter by salary"),
    posted_after: Optional[str] = Query(
        default=None, description="Filter jobs posted after this date (YYYY-MM-DD)"
    ),
    posted_before: Optional[str] = Query(
        default=None, description="Filter jobs posted before this date (YYYY-MM-DD)"
    ),
    sort_by: Optional[str] = Query(
        default="date_created", description="Field to sort by"
    ),
    order: Optional[str] = Query(
        default="desc", regex="^(asc|desc)$", description="Sort order: asc or desc"
    ),
    q: Optional[str] = Query(
        default=None, description="Search keywords (comma-separated)"
    ),
):
    """
    Get jobs with pagination, filtering, sorting, and search capabilities.

    - **limit**: Maximum number of jobs to return (default: 10, max: 100)
    - **offset**: Number of jobs to skip for pagination
    - **page**: Page number (alternative to offset, 1-based)
    - **salary**: Filter by salary
    - **posted_after**: Filter jobs posted after date (YYYY-MM-DD format)
    - **posted_before**: Filter jobs posted before date (YYYY-MM-DD format)
    - **sort_by**: Field to sort by (default: date_created)
    - **order**: Sort order - 'asc' or 'desc' (default: desc)
    - **q**: Search keywords in title and job_overview (comma-separated)
    """
    try:
        if page is not None:
            if page < 1:
                raise HTTPException(status_code=400, detail="Page number must be >= 1")
            offset = (page - 1) * limit

        valid_sort_fields = [
            "id",
            "job_id",
            "date_created",
        ]
        if sort_by and sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}",
            )

        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if posted_after and not re.match(date_pattern, posted_after):
            raise HTTPException(
                status_code=400, detail="posted_after must be in YYYY-MM-DD format"
            )
        if posted_before and not re.match(date_pattern, posted_before):
            raise HTTPException(
                status_code=400, detail="posted_before must be in YYYY-MM-DD format"
            )

        if q:
            q = re.sub(r"[^\w\s,.-]", "", q.strip())

        retry_count = 0

        while retry_count <= RETRY_COUNTS:
            try:
                query = db.query(Job)

                filters = []

                if salary:
                    salary = salary.strip()
                    filters.append(func.lower(Job.salary).like(f"%{salary.lower()}%"))

                if posted_after:
                    filters.append(Job.date_created >= posted_after)

                if posted_before:
                    filters.append(Job.date_created <= posted_before)

                if filters:
                    query = query.filter(and_(*filters))

                if sort_by:
                    sort_column = getattr(Job, sort_by)
                    if order == "desc":
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))
                else:
                    query = query.order_by(desc(Job.date_created))

                total_count = query.count()
                jobs = query.offset(offset).limit(limit).all()

                if q:
                    keywords = [
                        keyword.strip().lower()
                        for keyword in q.split(",")
                        if keyword.strip()
                    ]

                    filtered_jobs = []
                    for job in jobs:
                        job_title = (job.title or "").strip().lower()
                        job_overview = (job.job_overview or "").strip().lower()

                        match_found = False
                        for keyword in keywords:
                            if keyword in job_title or keyword in job_overview:
                                match_found = True
                                break

                        if match_found:
                            filtered_jobs.append(job)

                    jobs = filtered_jobs

                total_pages = (total_count + limit - 1) // limit
                current_page = (offset // limit) + 1
                has_next = offset + limit < total_count
                has_prev = offset > 0

                return {
                    "jobs": jobs,
                    "pagination": {
                        "total_count": total_count,
                        "total_pages": total_pages,
                        "current_page": current_page,
                        "limit": limit,
                        "offset": offset,
                        "has_next": has_next,
                        "has_prev": has_prev,
                    },
                    "filters_applied": {
                        "salary": salary,
                        "posted_after": posted_after,
                        "posted_before": posted_before,
                        "search_query": q,
                        "sort_by": sort_by,
                        "order": order,
                    },
                }

            except (DBAPIError, OperationalError, SQLAlchemyError) as db_error:
                error_str = str(db_error).lower()
                if (
                    "stream not found" in error_str
                    or "hrana" in error_str
                    or "connection" in error_str
                ) and retry_count < RETRY_COUNTS:

                    logger.warning(
                        f"Database connection error on attempt {retry_count + 1}/{RETRY_COUNTS + 1}: {db_error}"
                    )
                    retry_count += 1

                    db = handle_db_connection_error(db_error, db)
                    continue
                else:
                    raise
    except HTTPException:
        raise
    except (DBAPIError, OperationalError, SQLAlchemyError) as db_error:
        logger.error(f"Database error retrieving jobs: {str(db_error)}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable. Please try again.",
        )
    except Exception as e:
        logger.error(f"Error retrieving jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
def health_check():
    return {"status": "ok"}
