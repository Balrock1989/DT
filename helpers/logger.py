import logging

log = logging.getLogger("gui")

"""конфиг для логирования"""
def configure_logging():
    log.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%d-%m-%Y,%H:%M"))
    stream_handler.setLevel(logging.DEBUG)
    log.addHandler(stream_handler)
    file_handler = logging.FileHandler(filename="gui.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%d-%m-%Y,%H:%M"))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

