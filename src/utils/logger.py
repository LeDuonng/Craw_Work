#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module quản lý log của ứng dụng
"""

import os
import logging
from datetime import datetime
from .config import DEBUG_MODE, OUTPUT_DIR

# Tạo thư mục logs nếu chưa tồn tại
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Tạo tên file log dựa trên ngày hiện tại
log_filename = os.path.join(LOGS_DIR, f"crawwork_{datetime.now().strftime('%Y%m%d')}.log")

# Cấu hình logger
logger = logging.getLogger("crawwork")
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

# Tạo file handler
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

# Tạo console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

# Tạo formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Thêm handler vào logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger():
    """
    Trả về logger của ứng dụng
    """
    return logger 