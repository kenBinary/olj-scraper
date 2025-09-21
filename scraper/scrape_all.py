import requests
from bs4 import BeautifulSoup
import config.urls
from objects.JobLink import JobLink
import re
import random
from config.user_agents import user_agents


def scrape_all_job_listings() -> list[JobLink]:
    headers = {
        "User-Agent": random.choice(user_agents),
    }

    response = requests.get(
        config.urls.BASE_JOB_SEARCH_URL, headers=headers, timeout=30
    )

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links: list[JobLink] = []

        for link in soup.find_all("a", href=True):
            url = link["href"]
            if re.match(r"^/jobseekers/job/\d+$", url):
                job_id = url.split("/")[-1]
                job_link = JobLink(url=config.urls.BASE_URL + url, job_id=job_id)
                links.append(job_link)
        return links
    else:
        raise Exception(
            f"Failed to fetch job listings. Status code: {response.status_code}"
        )
