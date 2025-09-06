
# OLJ Scraper

Scrapes all job listings from [OnlineJobs.ph](https://www.onlinejobs.ph), stores them in a local or remote SQLite database, and can generate job summaries using the DeepSeek V3.1 model via OpenRouter.

## Features
- Scrapes all job listings from OnlineJobs.ph
- Stores job data in a Truso SQLite database
- Generates job summaries using DeepSeek V3.1 (OpenRouter)
- CLI options for development, production, and test modes

## Requirements
Uses Python3

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup
1. **Database Tables**
	 - Create tables:
		 ```bash
		 python -m scripts.create_tables --dev   # Local DB
		 python -m scripts.create_tables --prod  # Remote DB
		 ```
	 - Remove tables:
		 ```bash
		 python -m scripts.table_cleanup --dev   # Local DB
		 python -m scripts.table_cleanup --prod  # Remote DB
		 ```

2. **Environment Variables**
	 - Create a `.env` file in the root directory and add your DeepSeek API key:
		 ```env
		 DEEPSEEK_V3_OPENROUTER_API_KEY=your_api_key_here
         TURSO_DATABASE_URL=your_turso_db_url_here
         TURSO_AUTH_TOKEN=your_turso_auth_token_here
		 ```

## Usage
Run the scraper via CLI:

```bash
python main.py --dev      # Development mode
python main.py --prod     # Production mode
python main.py --test     # Test mode (scrapes only 3 jobs)
```

### CLI Options
- `--dev`: Use local database
- `--prod`: Use remote database
- `--test`: Scrape only 3 jobs for testing

## Configuration
- Job scraping URLs are defined in `config/urls.py`
- Arguments are initialized in `utils/args_init.py`
- Logging is configured in `services/logger/logger_config.py`

## DeepSeek Summaries
Summaries are generated using the DeepSeek V3.1 model via OpenRouter. Make sure your API key is set in `.env`.

## Project Structure
- `main.py`: Entry point for scraping
- `scripts/`: Table creation and cleanup scripts
- `db/`: Database models, engine, and repository
- `scraper/`: Scraping logic
- `services/openrouter/DeepSeek.py`: DeepSeek client integration

## Example
```bash
python main.py --dev
```

## Scripts
```bash
python -m scripts.remove_nulls --dev   # Local DB
python -m scripts.remove_nulls --prod  # Remote DB
```