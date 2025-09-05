def get_title(soup):
    title_element = soup.find("title")
    if title_element is None:
        return None
    return title_element.get_text(strip=True)


def get_work_type(soup):
    work_type_header = soup.find("h3", string="TYPE OF WORK")
    if work_type_header is None:
        return None
    p_tag_work_type = work_type_header.find_next("p")
    if p_tag_work_type is None:
        return None
    work_type = p_tag_work_type.text.strip()
    return work_type


def get_salary(soup):
    salary_header = soup.find("h3", string="SALARY")
    if salary_header is None:
        return None
    p_tag_salary = salary_header.find_next("p")
    if p_tag_salary is None:
        return None
    salary = p_tag_salary.text.strip()
    return salary


def get_hours_per_week(soup):
    hours_per_week_header = soup.find("h3", string="HOURS PER WEEK")
    if hours_per_week_header is None:
        return None
    p_tag_hours_per_week = hours_per_week_header.find_next("p")
    if p_tag_hours_per_week is None:
        return None
    hours_per_week = p_tag_hours_per_week.text.strip()
    return hours_per_week


def get_job_overview(soup):
    job_description_element = soup.find("p", id="job-description")
    if job_description_element is None:
        return None
    job_overview = job_description_element.get_text(separator="\n").strip()
    return job_overview
