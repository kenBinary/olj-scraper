import random
import time
import asyncio
from typing import List
from scraper.scrape_all import scrape_all_job_listings
from scraper.job_detail_scraper import scrape_job_detail
from db.models.Job import Job
from db.session.session import create_session_factory
from db.engine.engine import engine_init_local, engine_init_remote
from db.repository import job_repository
from services.logger.logger_config import Logger
from services.openrouter.DeepSeek import (
    init_async_deepseek_client,
    generate_summaries_async,
)
from utils.args_init import init_cli_args


def main():
    args = init_cli_args()
    print(f"Running in {'development' if args.dev else 'production'} mode")

    logger = Logger("main").get()
    logger.info("Starting job scraper application")
    try:
        logger.info("Scraping all job listings...")
        job_list = scrape_all_job_listings()
        logger.info(f"Scraped {len(job_list)} job listings")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    if args.test:
        logger.info("Test mode enabled: Limiting to 3 jobs")
        job_list = job_list[:3]

    jobs: List[Job] = []
    for job in job_list:
        jobDetail = scrape_job_detail(job.job_id, logger)
        jobs.append(jobDetail)
        time.sleep(random.uniform(1, 4))

    logger.info("Generating job summaries asynchronously...")
    start_time = time.time()
    asyncOpenai_client = init_async_deepseek_client()
    asyncio.run(generate_summaries_async(asyncOpenai_client, jobs))
    end_time = time.time()
    logger.info(
        f"Generated {len(jobs)} summaries in {end_time - start_time:.2f} seconds"
    )

    logger.info("Inserting jobs into the database...")
    if args.prod:
        logger.info("Using remote database")
        engine = engine_init_remote()
        SessionLocal = create_session_factory(engine)
    else:
        logger.info("Using local database")
        engine = engine_init_local()
        SessionLocal = create_session_factory(engine)

    with SessionLocal() as session:
        for job in jobs:
            existing_job = job_repository.get_job_by_job_id(session, job.job_id)
            if existing_job:
                logger.warning(
                    f"Job with job_id {job.job_id} already exists. Skipping insertion."
                )
                continue
            job_repository.add_job(session, job)

        session.commit()
    logger.info(f"Inserted {len(jobs)} jobs into the database.")


if __name__ == "__main__":
    main()
