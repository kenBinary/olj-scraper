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
from services.google_ai.Gemini import (
    init_gemini_client,
    generate_summaries_async,
)
from utils.args_init import init_cli_args
from utils.remove_nulls import remove_null_entries


def main():
    args = init_cli_args()
    print(f"Running in {'development' if args.dev else 'production'} mode")

    start_time_scraping = time.time()
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
    for index, job in enumerate(job_list, start=1):
        jobDetail = scrape_job_detail(
            job.job_id,
            index,
            logger,
        )
        jobs.append(jobDetail)
        time.sleep(1)

    logger.info("Generating job summaries asynchronously...")
    start_time = time.time()
    asyncGemini_client = init_gemini_client()
    asyncio.run(generate_summaries_async(asyncGemini_client, jobs))
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

    jobs_added = 0
    with SessionLocal() as session:
        for job in jobs:
            existing_job = job_repository.get_job_by_job_id(session, job.job_id)
            if existing_job:
                logger.warning(
                    f"Job with job_id {job.job_id} already exists. Skipping insertion."
                )
                continue
            jobs_added += 1
            job_repository.add_job(session, job)

        session.commit()
    logger.info(f"Inserted {jobs_added} jobs into the database.")
    logger.info(f"Ignored {len(jobs) - jobs_added} duplicate jobs.")
    end_time_scraping = time.time()
    logger.info(
        f"Total execution time: {end_time_scraping - start_time_scraping:.2f} seconds"
    )
    remove_null_entries(logger, env="prod" if args.prod else "dev")


if __name__ == "__main__":
    main()
