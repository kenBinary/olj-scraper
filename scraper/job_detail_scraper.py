from datetime import datetime
import requests
from bs4 import BeautifulSoup
import config.urls
from db.models.Job import Job
import parser.parsers as parsers
import random
from config.user_agents import user_agents


def scrape_job_detail(job_id, index, logger) -> Job:
    logger.info(f"Job {index}: Scraping job detail for Job ID: {job_id}")
    headers = {
        "User-Agent": random.choice(user_agents),
    }
    url = config.urls.BASE_JOB_DETAIL_URL + str(job_id)

    try:
        response = requests.get(url, headers=headers, timeout=30)
    except Exception as e:
        logger.error(f"Request failed for Job ID {job_id}: {e}")
        return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        title = parsers.get_title(soup)
        work_type = parsers.get_work_type(soup)
        salary = parsers.get_salary(soup)
        hours_per_week = parsers.get_hours_per_week(soup)
        job_overview = parsers.get_job_overview(soup)

        job = Job(
            job_id=job_id,
            title=title,
            work_type=work_type,
            salary=salary,
            hours_per_week=hours_per_week,
            job_overview=job_overview,
            raw_text=response.text,
            link=url,
            date_created=datetime.now().isoformat(),
        )
        return job
    else:
        logger.error(
            f"Failed to retrieve job details for Job ID {job_id}. Status code: {response.status_code}"
        )
        return None
