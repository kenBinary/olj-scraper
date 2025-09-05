from sqlalchemy import Column, Integer, String, Text
from db.models.Base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    work_type = Column(String, nullable=True)
    salary = Column(String, nullable=True)
    hours_per_week = Column(String, nullable=True)
    job_overview = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    link = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    date_created = Column(String, nullable=True)

    def __str__(self):
        return f"""
        Job ID: {self.job_id}
        Title: {self.title}
        Work Type: {self.work_type}
        Salary: {self.salary}
        Hours per Week: {self.hours_per_week}
        Job Overview: {self.job_overview}
        Summary: {self.summary}
        """

    def str_no_summary(self):
        return f"""
        Job ID: {self.job_id}
        Title: {self.title}
        Work Type: {self.work_type}
        Salary: {self.salary}
        Hours per Week: {self.hours_per_week}
        Job Overview: {self.job_overview}
        """
