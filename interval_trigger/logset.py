import logging
import logging.handlers

def loggers():
    """
    cd /etc/logrotate.d
    vi web.logger
    /home/system/logs/web/web.log {
    copytruncate
    daily
    dateext
    missingok
    rotate 365
    }
    :return:
    """
    filename = 'interval'
    logger = logging.getLogger('interval')
    if len(logger.handlers) > 0:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s  %(filename)s:%(lineno)s %(funcName)s - %(levelname)s1() ] %(message)s')
    rotate_handler = logging.handlers.TimedRotatingFileHandler(filename=f"logs/{filename}.log", when="midnight", interval=1, backupCount=10, encoding="utf-8")
    rotate_handler.setFormatter(formatter)
    logger.addHandler(rotate_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
