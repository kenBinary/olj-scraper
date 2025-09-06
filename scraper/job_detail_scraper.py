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
        "Sec-CH-UA": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    url = config.urls.BASE_JOB_DETAIL_URL + str(job_id)
    response = requests.get(url, headers=headers)

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
