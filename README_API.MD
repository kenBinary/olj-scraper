# OLJ Scraper API

API for the jobs scraped from [OnlineJobs.ph](https://www.onlinejobs.ph).

## Quick Start

### Prerequisites
- Python 3.8+
- Dependencies from `requirements.txt`

### Installation
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file in the root directory:
```env
API_ENV=dev                           # Use 'prod' for remote database
TURSO_DATABASE_URL=your_turso_db_url_here    # For production
TURSO_AUTH_TOKEN=your_turso_auth_token_here  # For production
```

### Running the API
```bash
# Development mode (local database)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production mode (set API_ENV=prod in .env)
uvicorn api:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints

#### Get Jobs
```http
GET /api/jobs
```

Retrieve job listings with filtering, searching, sorting, and pagination.

##### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Number of jobs to return (1-100) |
| `offset` | integer | 0 | Number of jobs to skip |
| `page` | integer | - | Page number (alternative to offset, 1-based) |
| `salary` | string | - | Filter by salary (partial match) |
| `posted_after` | string | - | Filter jobs posted after date (YYYY-MM-DD) |
| `posted_before` | string | - | Filter jobs posted before date (YYYY-MM-DD) |
| `sort_by` | string | date_created | Field to sort by |
| `order` | string | desc | Sort order: `asc` or `desc` |
| `q` | string | - | Search keywords (comma-separated) |

##### Valid Sort Fields
- `id` - Job ID
- `job_id` - External job identifier  
- `title` - Job title
- `work_type` - Type of work
- `salary` - Salary information
- `hours_per_week` - Working hours
- `date_created` - Creation date

##### Example Requests

**Basic request:**
```bash
curl "http://localhost:8000/api/jobs?limit=5"
```

**Search with pagination:**
```bash
curl "http://localhost:8000/api/jobs?q=developer,python&page=1&limit=10"
```

**Filter by date range and salary:**
```bash
curl "http://localhost:8000/api/jobs?posted_after=2024-01-01&salary=1000&sort_by=date_created&order=desc"
```

**Multiple keyword search:**
```bash
curl "http://localhost:8000/api/jobs?q=web developer,full-time,remote"
```

##### Response Format
```json
{
  "jobs": [
    {
      "id": 1,
      "job_id": "job_123456",
      "title": "Python Developer",
      "work_type": "Full-time",
      "salary": "$50,000 - $70,000",
      "hours_per_week": "40",
      "job_overview": "We are looking for an experienced Python developer...",
      "summary": "AI-generated summary of the job posting...",
      "link": "https://www.onlinejobs.ph/jobseekers/jobinfo/123456",
      "raw_text": "Full raw job posting text...",
      "date_created": "2024-01-15"
    }
  ],
  "pagination": {
    "total_count": 150,
    "total_pages": 15,
    "current_page": 1,
    "limit": 10,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "salary": null,
    "posted_after": null,
    "posted_before": null,
    "search_query": "python",
    "sort_by": "date_created",
    "order": "desc"
  }
}
```

#### Health Check
```http
GET /health
```

Simple health check endpoint that returns server status.

**Response:**
```json
{
  "status": "ok"
}
```
## Search Capabilities

supports powerful search functionality:

- **Keyword Search**: Search in job titles and descriptions
- **Multiple Keywords**: Use comma-separated keywords
- **Partial Matching**: Finds partial matches in text
- **Case Insensitive**: Search is not case-sensitive

Example searches:
- `q=python` - Find jobs mentioning Python
- `q=developer,full-time` - Find developer jobs that are full-time
- `q=web,react,javascript` - Find web development jobs with React and JavaScript

## Project Integration

This API works alongside the main OLJ Scraper project:

1. **Data Source**: Job data is populated by running the scraper (`main.py`)
2. **Database**: Shares the same database models and engine configuration

To populate the database before using the API:
```bash
python main.py --dev   
python main.py --prod 
```