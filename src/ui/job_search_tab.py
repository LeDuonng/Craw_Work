#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module chứa giao diện tab tìm việc
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QSpinBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView

from src.utils.config import (
    JOB_SITES, EXPERIENCE_LEVELS,
    JOB_TYPES, WORK_MODES
)
from src.utils.logger import get_logger
from src.modules.job_search.crawler import JobCrawler
from src.modules.job_search.processor import JobProcessor

# Khởi tạo logger
logger = get_logger()

class JobSearchTab(QWidget):
    """
    Tab tìm việc
    """
    
    # Định nghĩa các signal
    error_occurred = pyqtSignal(str)
    info_message = pyqtSignal(str)
    
    def __init__(self):
        """
        Khởi tạo tab tìm việc
        """
        super().__init__()
        
        # Khởi tạo các thành phần
        self.crawler = None
        self.processor = None
        
        # Thiết lập giao diện
        self._setup_ui()
        
        # Kết nối các signal
        self._connect_signals()
        
        logger.info("Đã khởi tạo tab tìm việc")
    
    def _setup_ui(self):
        """
        Thiết lập giao diện
        """
        # Tạo layout chính
        main_layout = QVBoxLayout(self)
        
        # Tạo form nhập liệu
        form_layout = QGridLayout()
        
        # Từ khóa tìm kiếm
        form_layout.addWidget(QLabel("Công việc cần tìm:"), 0, 0)
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")
        form_layout.addWidget(self.keyword_input, 0, 1, 1, 2)
        
        # Địa điểm người dùng
        form_layout.addWidget(QLabel("Địa điểm của bạn:"), 1, 0)
        location_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Nhập địa chỉ hoặc chọn trên bản đồ...")
        location_layout.addWidget(self.location_input)
        self.map_button = QPushButton("Chọn trên bản đồ")
        location_layout.addWidget(self.map_button)
        form_layout.addLayout(location_layout, 1, 1, 1, 2)
        
        # Số lượng link cần crawl
        form_layout.addWidget(QLabel("Số lượng link cần crawl:"), 2, 0)
        self.max_pages_input = QSpinBox()
        self.max_pages_input.setMinimum(1)
        self.max_pages_input.setMaximum(20)
        self.max_pages_input.setValue(5)
        form_layout.addWidget(self.max_pages_input, 2, 1)
        
        # Các trang tuyển dụng
        form_layout.addWidget(QLabel("Trang tuyển dụng:"), 3, 0)
        self.sites_combo = QComboBox()
        self.sites_combo.addItem("Tất cả")
        for site_key, site in JOB_SITES.items():
            self.sites_combo.addItem(site['name'], site_key)
        form_layout.addWidget(self.sites_combo, 3, 1)
        
        # Kinh nghiệm
        form_layout.addWidget(QLabel("Kinh nghiệm:"), 4, 0)
        self.experience_combo = QComboBox()
        self.experience_combo.addItem("Tất cả")
        self.experience_combo.addItems(EXPERIENCE_LEVELS)
        form_layout.addWidget(self.experience_combo, 4, 1)
        
        # Loại công việc
        form_layout.addWidget(QLabel("Loại công việc:"), 5, 0)
        self.job_type_combo = QComboBox()
        self.job_type_combo.addItem("Tất cả")
        self.job_type_combo.addItems(JOB_TYPES)
        form_layout.addWidget(self.job_type_combo, 5, 1)
        
        # Chế độ làm việc
        form_layout.addWidget(QLabel("Chế độ làm việc:"), 6, 0)
        self.work_mode_combo = QComboBox()
        self.work_mode_combo.addItem("Tất cả")
        self.work_mode_combo.addItems(WORK_MODES)
        form_layout.addWidget(self.work_mode_combo, 6, 1)
        
        # Khoảng cách tối đa
        form_layout.addWidget(QLabel("Khoảng cách tối đa (km):"), 7, 0)
        self.distance_input = QSpinBox()
        self.distance_input.setMinimum(0)
        self.distance_input.setMaximum(100)
        self.distance_input.setValue(20)
        form_layout.addWidget(self.distance_input, 7, 1)
        
        # Mức lương
        salary_layout = QHBoxLayout()
        salary_layout.addWidget(QLabel("Mức lương (triệu):"))
        self.salary_min_input = QSpinBox()
        self.salary_min_input.setMinimum(0)
        self.salary_min_input.setMaximum(1000)
        salary_layout.addWidget(self.salary_min_input)
        salary_layout.addWidget(QLabel("-"))
        self.salary_max_input = QSpinBox()
        self.salary_max_input.setMinimum(0)
        self.salary_max_input.setMaximum(1000)
        salary_layout.addWidget(self.salary_max_input)
        form_layout.addLayout(salary_layout, 8, 0, 1, 3)
        
        # Kỹ năng yêu cầu
        form_layout.addWidget(QLabel("Kỹ năng yêu cầu:"), 9, 0)
        self.skills_input = QTextEdit()
        self.skills_input.setPlaceholderText("Nhập các kỹ năng, mỗi kỹ năng một dòng...")
        self.skills_input.setMaximumHeight(100)
        form_layout.addWidget(self.skills_input, 9, 1, 1, 2)
        
        main_layout.addLayout(form_layout)
        
        # Tạo các nút chức năng
        button_layout = QHBoxLayout()
        
        self.crawl_links_button = QPushButton("Crawl Link Tuyển Dụng")
        button_layout.addWidget(self.crawl_links_button)
        
        self.crawl_details_button = QPushButton("Crawl Dữ Liệu Chi Tiết & Xuất CSV")
        self.crawl_details_button.setEnabled(False)
        button_layout.addWidget(self.crawl_details_button)
        
        main_layout.addLayout(button_layout)
        
        # Tạo progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Tạo bảng kết quả
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(8)
        self.result_table.setHorizontalHeaderLabels([
            "Tiêu đề", "Công ty", "Địa điểm",
            "Mức lương", "Kinh nghiệm", "Loại công việc",
            "Chế độ làm việc", "Khoảng cách (km)"
        ])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.result_table)
        
        # Tạo widget bản đồ
        self.map_widget = QWebEngineView()
        self.map_widget.setVisible(False)
        main_layout.addWidget(self.map_widget)
    
    def _connect_signals(self):
        """
        Kết nối các signal
        """
        # Kết nối các nút
        self.map_button.clicked.connect(self._show_map)
        self.crawl_links_button.clicked.connect(self._crawl_links)
        self.crawl_details_button.clicked.connect(self._crawl_details)
        
        # Kết nối các sự kiện thay đổi giá trị
        self.salary_min_input.valueChanged.connect(self._update_salary_range)
        self.salary_max_input.valueChanged.connect(self._update_salary_range)
    
    def _show_map(self):
        """
        Hiển thị bản đồ để chọn vị trí
        """
        # TODO: Implement map view
        pass
    
    def _crawl_links(self):
        """
        Crawl danh sách link tuyển dụng
        """
        # Kiểm tra từ khóa
        keyword = self.keyword_input.text().strip()
        if not keyword:
            self.error_occurred.emit("Vui lòng nhập từ khóa tìm kiếm")
            return
        
        try:
            # Khởi tạo crawler
            self.crawler = JobCrawler()
            
            # Lấy các tham số
            max_pages = self.max_pages_input.value()
            site_key = self.sites_combo.currentData()
            sites = [site_key] if site_key else None
            
            # Hiển thị progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Crawl link
            job_links = self.crawler.crawl_job_links(
                keyword=keyword,
                max_pages=max_pages,
                sites=sites
            )
            
            # Cập nhật trạng thái
            self.crawl_details_button.setEnabled(True)
            self.progress_bar.setValue(100)
            
            # Thông báo kết quả
            self.info_message.emit(f"Đã crawl được {len(job_links)} link tuyển dụng")
        
        except Exception as e:
            logger.error(f"Lỗi khi crawl link: {e}")
            self.error_occurred.emit(str(e))
        
        finally:
            # Đóng crawler
            if self.crawler:
                self.crawler.close()
    
    def _crawl_details(self):
        """
        Crawl chi tiết công việc và xuất CSV
        """
        try:
            # Khởi tạo crawler và processor
            self.crawler = JobCrawler()
            self.processor = JobProcessor(
                user_location=self.location_input.text().strip()
            )
            
            # Hiển thị progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Crawl chi tiết
            job_details = self.crawler.crawl_job_details()
            
            # Xử lý dữ liệu
            filters = self._get_filters()
            processed_jobs = self.processor.process_jobs(
                jobs=job_details,
                filters=filters
            )
            
            # Hiển thị kết quả
            self._display_results(processed_jobs)
            
            # Cập nhật progress bar
            self.progress_bar.setValue(100)
            
            # Thông báo kết quả
            self.info_message.emit(f"Đã xử lý {len(processed_jobs)} công việc")
        
        except Exception as e:
            logger.error(f"Lỗi khi crawl chi tiết: {e}")
            self.error_occurred.emit(str(e))
        
        finally:
            # Đóng crawler
            if self.crawler:
                self.crawler.close()
    
    def _get_filters(self):
        """
        Lấy các bộ lọc từ giao diện
        
        Returns:
            dict: Các bộ lọc
        """
        filters = {}
        
        # Kinh nghiệm
        experience = self.experience_combo.currentText()
        if experience != "Tất cả":
            filters['experience'] = experience
        
        # Loại công việc
        job_type = self.job_type_combo.currentText()
        if job_type != "Tất cả":
            filters['job_type'] = job_type
        
        # Chế độ làm việc
        work_mode = self.work_mode_combo.currentText()
        if work_mode != "Tất cả":
            filters['work_mode'] = work_mode
        
        # Khoảng cách
        distance_max = self.distance_input.value()
        if distance_max > 0:
            filters['distance_max'] = distance_max
        
        # Mức lương
        salary_min = self.salary_min_input.value()
        if salary_min > 0:
            filters['salary_min'] = salary_min
        
        salary_max = self.salary_max_input.value()
        if salary_max > 0:
            filters['salary_max'] = salary_max
        
        # Kỹ năng
        skills = self.skills_input.toPlainText().strip()
        if skills:
            filters['skills'] = [s.strip() for s in skills.split('\n') if s.strip()]
        
        return filters
    
    def _display_results(self, jobs):
        """
        Hiển thị kết quả lên bảng
        
        Args:
            jobs (list): Danh sách công việc
        """
        # Xóa dữ liệu cũ
        self.result_table.setRowCount(0)
        
        # Thêm dữ liệu mới
        for job in jobs:
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            
            # Tiêu đề
            self.result_table.setItem(row, 0, QTableWidgetItem(job.get('title', '')))
            
            # Công ty
            self.result_table.setItem(row, 1, QTableWidgetItem(job.get('company', '')))
            
            # Địa điểm
            self.result_table.setItem(row, 2, QTableWidgetItem(job.get('location', '')))
            
            # Mức lương
            self.result_table.setItem(row, 3, QTableWidgetItem(job.get('salary', '')))
            
            # Kinh nghiệm
            self.result_table.setItem(row, 4, QTableWidgetItem(job.get('experience', '')))
            
            # Loại công việc
            self.result_table.setItem(row, 5, QTableWidgetItem(job.get('job_type', '')))
            
            # Chế độ làm việc
            self.result_table.setItem(row, 6, QTableWidgetItem(job.get('work_mode', '')))
            
            # Khoảng cách
            distance = job.get('distance')
            distance_text = f"{distance:.1f}" if distance else ""
            self.result_table.setItem(row, 7, QTableWidgetItem(distance_text))
    
    def _update_salary_range(self):
        """
        Cập nhật khoảng lương
        """
        min_value = self.salary_min_input.value()
        max_value = self.salary_max_input.value()
        
        if max_value > 0 and min_value > max_value:
            self.salary_max_input.setValue(min_value)
    
    def close(self):
        """
        Đóng tab
        """
        # Đóng crawler
        if self.crawler:
            self.crawler.close()
        
        super().close() 