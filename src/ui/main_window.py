#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module chứa cửa sổ chính của ứng dụng
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from src.utils.logger import get_logger
from .job_search_tab import JobSearchTab
from .cv_generator_tab import CVGeneratorTab

# Khởi tạo logger
logger = get_logger()

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
        self.setWindowTitle("CrawWork - Ứng dụng Tìm việc và Tạo CV")
        self.setMinimumSize(1200, 800)
        
        # Tạo widget trung tâm
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Tạo layout chính
        main_layout = QVBoxLayout(central_widget)
        
        # Tạo header
        header_layout = QHBoxLayout()
        logo_label = QLabel("CrawWork")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Tạo tab widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
        """)
        
        # Thêm các tab
        self.job_search_tab = JobSearchTab()
        tab_widget.addTab(self.job_search_tab, "Tìm việc")
        
        self.cv_generator_tab = CVGeneratorTab()
        tab_widget.addTab(self.cv_generator_tab, "Tạo CV")
        
        main_layout.addWidget(tab_widget)
        
        # Tạo footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        version_label = QLabel("v1.0.0")
        footer_layout.addWidget(version_label)
        main_layout.addLayout(footer_layout)
        
        # Kết nối các signal
        self._connect_signals()
        
        logger.info("Đã khởi tạo cửa sổ chính")
    
    def _connect_signals(self):
        """
        Kết nối các signal
        """
        # Kết nối signal từ tab tìm việc
        self.job_search_tab.error_occurred.connect(self._show_error)
        self.job_search_tab.info_message.connect(self._show_info)
        
        # Kết nối signal từ tab tạo CV
        self.cv_generator_tab.error_occurred.connect(self._show_error)
        self.cv_generator_tab.info_message.connect(self._show_info)
    
    def _show_error(self, message):
        """
        Hiển thị thông báo lỗi
        
        Args:
            message (str): Nội dung thông báo
        """
        QMessageBox.critical(self, "Lỗi", message)
    
    def _show_info(self, message):
        """
        Hiển thị thông báo thông tin
        
        Args:
            message (str): Nội dung thông báo
        """
        QMessageBox.information(self, "Thông báo", message)
    
    def closeEvent(self, event):
        """
        Xử lý sự kiện đóng cửa sổ
        """
        # Đóng các tab
        self.job_search_tab.close()
        self.cv_generator_tab.close()
        
        event.accept() 