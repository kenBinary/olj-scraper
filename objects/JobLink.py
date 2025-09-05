class JobLink:
    def __init__(self, url: str, job_id: str):
        self.url = url
        self.job_id = job_id

    def __repr__(self):
        return f"JobLink(url={self.url!r}, job_id={self.job_id!r})"
