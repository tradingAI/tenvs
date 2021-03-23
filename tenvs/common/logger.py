import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[%(lineno)d] %(levelname)s %(message)s')

logger = logging.getLogger()

logger_dir = os.getenv("TENVS_LOG_DIR")
if logger_dir is None or logger_dir == "":
    logger_dir = os.path.join("/tmp", "tenvs")
try:
    if not os.path.exists(logger_dir):
        os.makedirs(logger_dir)
except Exception as e:
    print("make dir error", e)
    import traceback
    traceback.print_exc()

handler = logging.FileHandler(os.path.join(logger_dir, "tenvs.log"))
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s[%(lineno)d] %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
