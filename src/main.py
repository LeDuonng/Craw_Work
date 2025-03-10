#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CrawWork - Ứng dụng Tìm việc và Tạo CV Tự động
"""

import os
import sys
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication

# Thêm thư mục gốc vào đường dẫn
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load biến môi trường từ file .env
load_dotenv()

# Import các module cần thiết
from src.ui.main_window import MainWindow

def main():
    """
    Hàm chính để khởi chạy ứng dụng
    """
    # Tạo thư mục output nếu chưa tồn tại
    output_dir = os.getenv("OUTPUT_DIR", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Khởi tạo ứng dụng PyQt
    app = QApplication(sys.argv)
    app.setApplicationName(os.getenv("APP_NAME", "CrawWork"))
    
    # Khởi tạo cửa sổ chính
    window = MainWindow()
    window.show()
    
    # Chạy ứng dụng
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 