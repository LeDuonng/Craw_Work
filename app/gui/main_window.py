"""
Main Window của ứng dụng
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QProgressBar,
    QFileDialog, QMessageBox, QGroupBox, QScrollArea, QSplitter,
    QDateEdit, QFrame, QGridLayout, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap
from app.gui.job_search_tab import JobSearchTab
from app.gui.cv_generator_tab import CVGeneratorTab
from app.utils.config import JOB_WEBSITES

class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng
    """
    
    def __init__(self):
        """
        Khởi tạo cửa sổ chính
        """
        super().__init__()
        
        # Thiết lập cửa sổ
        self.setWindowTitle("Ứng Dụng Cào Dữ Liệu Tuyển Dụng & Tạo CV Tự Động")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Thiết lập icon (nếu có)
        # self.setWindowIcon(QIcon("app/resources/icon.png"))
        
        # Thiết lập widget trung tâm
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Thiết lập layout chính
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Tạo tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Tạo các tab
        self.job_search_tab = JobSearchTab()
        self.cv_generator_tab = CVGeneratorTab()
        
        # Thêm các tab vào tab widget
        self.tab_widget.addTab(self.job_search_tab, "Tìm Kiếm Việc Làm")
        self.tab_widget.addTab(self.cv_generator_tab, "Tạo CV Tự Động")
        
        # Thiết lập thanh trạng thái
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Sẵn sàng")
        
        # Kết nối các tín hiệu
        self.connect_signals()
        
        # Áp dụng stylesheet
        self.apply_stylesheet()
    
    def connect_signals(self):
        """
        Kết nối các tín hiệu giữa các thành phần
        """
        # Kết nối tín hiệu từ tab tìm kiếm việc làm
        self.job_search_tab.status_message.connect(self.update_status)
        
        # Kết nối tín hiệu từ tab tạo CV
        self.cv_generator_tab.status_message.connect(self.update_status)
        
        # Kết nối tín hiệu giữa hai tab
        self.job_search_tab.job_selected.connect(self.cv_generator_tab.set_job_info)
    
    def update_status(self, message):
        """
        Cập nhật thanh trạng thái
        
        Args:
            message (str): Thông báo trạng thái
        """
        self.status_bar.showMessage(message)
    
    def apply_stylesheet(self):
        """
        Áp dụng stylesheet cho giao diện
        """
        # Thiết lập font chung
        app = QApplication.instance()
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        # Stylesheet chung
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                border-radius: 5px;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #cccccc;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #3a76d8;
            }
            
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
                border: 1px solid #4a86e8;
            }
            
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
            }
            
            QTableWidget::item {
                padding: 4px;
            }
            
            QTableWidget::item:selected {
                background-color: #e6f0ff;
                color: #000000;
            }
            
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 6px;
                border: none;
                border-right: 1px solid #cccccc;
                border-bottom: 1px solid #cccccc;
                font-weight: bold;
            }
            
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }
            
            QProgressBar::chunk {
                background-color: #4a86e8;
                width: 10px;
                margin: 0.5px;
            }
            
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 12px;
                font-weight: bold;
                background-color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: #333333;
            }
            
            QScrollArea {
                border: none;
            }
            
            QLabel {
                color: #333333;
            }
            
            QStatusBar {
                background-color: #f0f0f0;
                color: #333333;
                border-top: 1px solid #cccccc;
            }
        """)

def main():
    """
    Hàm chính để chạy ứng dụng
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 