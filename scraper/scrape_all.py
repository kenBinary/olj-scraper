import requests
from bs4 import BeautifulSoup
import config.urls
from objects.JobLink import JobLink
import re


def scrape_all_job_listings() -> list[JobLink]:
    response = requests.get(config.urls.BASE_JOB_SEARCH_URL)
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
        raise Exception("Failed to fetch job listings", response.status_code)
