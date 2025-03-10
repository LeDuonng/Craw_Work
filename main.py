"""
Ứng Dụng Cào Dữ Liệu Tuyển Dụng Việc Làm Thông Minh & Tạo CV Tự Động
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from app.gui.main_window import MainWindow

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Đảm bảo thư mục hiện tại là thư mục gốc của ứng dụng
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Log thông tin khởi động
    logger.info("Khởi động ứng dụng Cào Dữ Liệu Tuyển Dụng & Tạo CV Tự Động")
    logger.info("Sử dụng OpenAI Deep Search cho tìm kiếm việc làm thông minh")
    
    # Tạo ứng dụng
    app = QApplication(sys.argv)
    
    # Tạo cửa sổ chính
    window = MainWindow()
    
    # Hiển thị cửa sổ
    window.show()
    
    # Chạy ứng dụng
    sys.exit(app.exec_()) 