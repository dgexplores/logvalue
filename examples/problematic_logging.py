import logging

logger = logging.getLogger(__name__)

def process(user_id: int) -> None:
    print(f"processing {user_id}")
    logger.info("processed " + str(user_id))
