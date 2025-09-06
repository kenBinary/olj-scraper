from typing import List
from google import genai
from google.genai import types
import os
import asyncio
from dotenv import load_dotenv
from db.models.Job import Job
from .models import GeminiModels


def init_gemini_client():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    client = genai.Client()
    return client


# TODO: rotate models
def ask_model(client) -> str:
    response = client.models.generate_content(
        model=GeminiModels.GEMINI_2_5_FLASH_LITE,
        contents="What is the meaning of life?",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )
    return response.text


async def generate_summaries_async(client, jobs: List[Job]) -> None:
    tasks = []
    for job in jobs:
        task = generate_job_summary_async(client, job.job_overview, job.link)
        tasks.append((job, task))
    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

    for i, ((job, _), result) in enumerate(zip(tasks, results)):
        if isinstance(result, Exception):
            print(f"Error generating summary for job {job.job_id}: {result}")
            job.summary = "Summary generation failed"
        else:
            job.summary = result


async def generate_job_summary_async(client, job_info, apply_link=None) -> str:
    prompt = f"""
    You are a job summarization assistant.

    I will give you detailed information about a job posting. Your task is to generate a compact, Telegram-ready job notification message. The message should be:

    1. Scannable on mobile.
    2. Concise (no more than ~150 words).
    3. Include the following sections:
    - Job Title & Focus
    - Type & Hours
    - Salary
    - Company / Industry (optional)
    - Key Responsibilities (2-3 bullets max)
    - Key Requirements (2-3 bullets max)
    - Bonus Skills (if relevant)
    - Link / CTA (if provided)

    Use short, clear bullet points where appropriate. Keep formatting readable and professional. Do not include unnecessary details.
    IMPORTANT:
    - Do NOT include any preamble, introduction, or phrases like "Here is a compact Telegram-ready job summary" or "Summary:". 
    - Output ONLY the final Telegram message in the requested format.
    - Start directly with the job title or emoji heading.

    Here is the job information:

    {job_info}
    """
    if apply_link:
        prompt += f"\nApply here: {apply_link}"

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=GeminiModels.GEMINI_2_5_FLASH_LITE,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        ),
    )
    return response.text


def generate_job_summary(client, job_info, apply_link=None) -> str:
    prompt = f"""
    You are a job summarization assistant.

    I will give you detailed information about a job posting. Your task is to generate a compact, Telegram-ready job notification message. The message should be:

    1. Scannable on mobile.
    2. Concise (no more than ~150 words).
    3. Include the following sections:
    - Job Title & Focus
    - Type & Hours
    - Salary
    - Company / Industry (optional)
    - Key Responsibilities (2-3 bullets max)
    - Key Requirements (2-3 bullets max)
    - Bonus Skills (if relevant)
    - Link / CTA (if provided)

    Use short, clear bullet points where appropriate. Keep formatting readable and professional. Do not include unnecessary details.
    IMPORTANT:
    - Do NOT include any preamble, introduction, or phrases like "Here is a compact Telegram-ready job summary" or "Summary:". 
    - Output ONLY the final Telegram message in the requested format.
    - Start directly with the job title or emoji heading.

    Here is the job information:

    {job_info}
    """
    if apply_link:
        prompt += f"\nApply here: {apply_link}"

    response = client.models.generate_content(
        model=GeminiModels.GEMINI_2_5_FLASH_LITE,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )
    return response.text
