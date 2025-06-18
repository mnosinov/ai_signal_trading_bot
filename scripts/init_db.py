from sqlalchemy import create_engine
from bot.models.trade import Base
from bot.config.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger("db_init")


def initialize_database():
    try:
        engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


if __name__ == "__main__":
    initialize_database()
