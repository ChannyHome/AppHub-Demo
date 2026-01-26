from loguru import logger

def audit(message: str, **kwargs):
    logger.bind(audit=True, **kwargs).info(message)

def business_warn(message: str, **kwargs):
    logger.bind(biz=True, **kwargs).warning(message)

def business_error(message: str, **kwargs):
    logger.bind(biz=True, **kwargs).error(message)
