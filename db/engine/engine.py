from sqlalchemy import create_engine


def engine_init():
    return create_engine("sqlite:///data/olj-scraper.db")
