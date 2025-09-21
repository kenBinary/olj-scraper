from fastapi import Depends, FastAPI, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
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

        query = db.query(Job)

        filters = []

        if salary:
            salary = salary.strip()
            filters.append(func.lower(Job.salary).like(f"%{salary.lower()}%"))

        if posted_after:
            filters.append(Job.date_created >= posted_after)

        if posted_before:
            filters.append(Job.date_created <= posted_before)

        if q:
            keywords = [keyword.strip() for keyword in q.split(",") if keyword.strip()]
            search_filters = []

            for keyword in keywords:
                keyword_filter = or_(
                    func.trim(Job.title).like(f"%{keyword}%"),
                    func.trim(Job.job_overview).like(f"%{keyword}%"),
                )
                search_filters.append(keyword_filter)

            if search_filters:
                filters.append(or_(*search_filters))

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
def health_check():
    return {"status": "ok"}
