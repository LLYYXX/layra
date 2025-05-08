import logging
import sys
from .config import settings

# 创建日志记录器
logger = logging.getLogger("layra")
logger.setLevel(getattr(logging, settings.log_level.upper()))

# 创建文件处理器
file_handler = logging.FileHandler(settings.log_file, mode="a")
file_handler.setLevel(getattr(logging, settings.log_level.upper()))

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, settings.log_level.upper()))

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 防止日志记录被重复
logger.propagate = False
