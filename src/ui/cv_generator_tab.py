#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module chứa giao diện tab tạo CV
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QProgressBar, QDateEdit,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from datetime import datetime

from src.utils.logger import get_logger
from src.modules.cv_generator.generator import CVGenerator

# Khởi tạo logger
logger = get_logger()

class CVGeneratorTab(QWidget):
    """
    Tab tạo CV
    """
    
    # Định nghĩa các signal
    error_occurred = pyqtSignal(str)
    info_message = pyqtSignal(str)
    
    def __init__(self):
        """
        Khởi tạo tab tạo CV
        """
        super().__init__()
        
        # Khởi tạo các thành phần
        self.generator = CVGenerator()
        self.photo_path = None
        
        # Thiết lập giao diện
        self._setup_ui()
        
        # Kết nối các signal
        self._connect_signals()
        
        logger.info("Đã khởi tạo tab tạo CV")
    
    def _setup_ui(self):
        """
        Thiết lập giao diện
        """
        # Tạo layout chính
        main_layout = QVBoxLayout(self)
        
        # Tạo form nhập liệu
        form_layout = QGridLayout()
        
        # Thông tin cá nhân
        form_layout.addWidget(QLabel("THÔNG TIN CÁ NHÂN"), 0, 0, 1, 2)
        
        # Họ và tên
        form_layout.addWidget(QLabel("Họ và tên:"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập họ và tên...")
        form_layout.addWidget(self.name_input, 1, 1)
        
        # Email
        form_layout.addWidget(QLabel("Email:"), 2, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email...")
        form_layout.addWidget(self.email_input, 2, 1)
        
        # Số điện thoại
        form_layout.addWidget(QLabel("Số điện thoại:"), 3, 0)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại...")
        form_layout.addWidget(self.phone_input, 3, 1)
        
        # Địa chỉ
        form_layout.addWidget(QLabel("Địa chỉ:"), 4, 0)
        location_layout = QHBoxLayout()
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Nhập địa chỉ hoặc chọn trên bản đồ...")
        location_layout.addWidget(self.address_input)
        self.map_button = QPushButton("Chọn trên bản đồ")
        location_layout.addWidget(self.map_button)
        form_layout.addLayout(location_layout, 4, 1)
        
        # Ngày sinh
        form_layout.addWidget(QLabel("Ngày sinh:"), 5, 0)
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addWidget(self.birth_date_input, 5, 1)
        
        # Ảnh cá nhân
        form_layout.addWidget(QLabel("Ảnh cá nhân:"), 6, 0)
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel("Chưa chọn ảnh")
        photo_layout.addWidget(self.photo_label)
        self.photo_button = QPushButton("Chọn ảnh")
        photo_layout.addWidget(self.photo_button)
        form_layout.addLayout(photo_layout, 6, 1)
        
        # Kinh nghiệm làm việc
        form_layout.addWidget(QLabel("KINH NGHIỆM LÀM VIỆC"), 7, 0, 1, 2)
        self.experience_input = QTextEdit()
        self.experience_input.setPlaceholderText("Nhập kinh nghiệm làm việc...")
        self.experience_input.setMinimumHeight(100)
        form_layout.addWidget(self.experience_input, 8, 0, 1, 2)
        
        # Học vấn
        form_layout.addWidget(QLabel("HỌC VẤN"), 9, 0, 1, 2)
        self.education_input = QTextEdit()
        self.education_input.setPlaceholderText("Nhập thông tin học vấn...")
        self.education_input.setMinimumHeight(100)
        form_layout.addWidget(self.education_input, 10, 0, 1, 2)
        
        # Kỹ năng
        form_layout.addWidget(QLabel("KỸ NĂNG"), 11, 0, 1, 2)
        self.skills_input = QTextEdit()
        self.skills_input.setPlaceholderText("Nhập các kỹ năng, mỗi kỹ năng một dòng...")
        self.skills_input.setMinimumHeight(100)
        form_layout.addWidget(self.skills_input, 12, 0, 1, 2)
        
        # Thông tin bổ sung
        form_layout.addWidget(QLabel("THÔNG TIN BỔ SUNG"), 13, 0, 1, 2)
        self.additional_info_input = QTextEdit()
        self.additional_info_input.setPlaceholderText("Nhập thông tin bổ sung (chứng chỉ, dự án, sở thích...)...")
        self.additional_info_input.setMinimumHeight(100)
        form_layout.addWidget(self.additional_info_input, 14, 0, 1, 2)
        
        main_layout.addLayout(form_layout)
        
        # Tạo các nút chức năng
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Tạo CV")
        button_layout.addWidget(self.generate_button)
        
        self.export_docx_button = QPushButton("Xuất DOCX")
        self.export_docx_button.setEnabled(False)
        button_layout.addWidget(self.export_docx_button)
        
        self.export_pdf_button = QPushButton("Xuất PDF")
        self.export_pdf_button.setEnabled(False)
        button_layout.addWidget(self.export_pdf_button)
        
        main_layout.addLayout(button_layout)
        
        # Tạo progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
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
        self.photo_button.clicked.connect(self._choose_photo)
        self.generate_button.clicked.connect(self._generate_cv)
        self.export_docx_button.clicked.connect(self._export_docx)
        self.export_pdf_button.clicked.connect(self._export_pdf)
    
    def _show_map(self):
        """
        Hiển thị bản đồ để chọn vị trí
        """
        # TODO: Implement map view
        pass
    
    def _choose_photo(self):
        """
        Chọn ảnh cá nhân
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Chọn ảnh",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.photo_path = file_path
            self.photo_label.setText(os.path.basename(file_path))
    
    def _generate_cv(self):
        """
        Tạo nội dung CV
        """
        # Kiểm tra thông tin bắt buộc
        if not self._validate_inputs():
            return
        
        try:
            # Hiển thị progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Lấy thông tin người dùng
            user_info = self._get_user_info()
            
            # Tạo nội dung CV
            self.cv_content = self.generator.generate_cv_content(user_info)
            
            if self.cv_content:
                # Cập nhật trạng thái
                self.export_docx_button.setEnabled(True)
                self.export_pdf_button.setEnabled(True)
                self.progress_bar.setValue(100)
                
                # Thông báo thành công
                self.info_message.emit("Đã tạo nội dung CV thành công")
            else:
                self.error_occurred.emit("Không thể tạo nội dung CV")
        
        except Exception as e:
            logger.error(f"Lỗi khi tạo CV: {e}")
            self.error_occurred.emit(str(e))
    
    def _export_docx(self):
        """
        Xuất CV ra file DOCX
        """
        try:
            # Mở dialog chọn nơi lưu file
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "Lưu CV",
                f"CV_{self.name_input.text().replace(' ', '_')}.docx",
                "Word Files (*.docx)"
            )
            
            if file_path:
                # Xuất file
                result = self.generator.export_to_docx(
                    self.cv_content,
                    filename=file_path
                )
                
                if result:
                    self.info_message.emit(f"Đã xuất CV ra file {file_path}")
                else:
                    self.error_occurred.emit("Không thể xuất file DOCX")
        
        except Exception as e:
            logger.error(f"Lỗi khi xuất file DOCX: {e}")
            self.error_occurred.emit(str(e))
    
    def _export_pdf(self):
        """
        Xuất CV ra file PDF
        """
        try:
            # Mở dialog chọn nơi lưu file
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "Lưu CV",
                f"CV_{self.name_input.text().replace(' ', '_')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Xuất file
                result = self.generator.export_to_pdf(
                    self.cv_content,
                    filename=file_path,
                    photo_path=self.photo_path
                )
                
                if result:
                    self.info_message.emit(f"Đã xuất CV ra file {file_path}")
                else:
                    self.error_occurred.emit("Không thể xuất file PDF")
        
        except Exception as e:
            logger.error(f"Lỗi khi xuất file PDF: {e}")
            self.error_occurred.emit(str(e))
    
    def _validate_inputs(self):
        """
        Kiểm tra thông tin đầu vào
        
        Returns:
            bool: Kết quả kiểm tra
        """
        # Kiểm tra họ tên
        if not self.name_input.text().strip():
            self.error_occurred.emit("Vui lòng nhập họ và tên")
            return False
        
        # Kiểm tra email
        if not self.email_input.text().strip():
            self.error_occurred.emit("Vui lòng nhập email")
            return False
        
        # Kiểm tra số điện thoại
        if not self.phone_input.text().strip():
            self.error_occurred.emit("Vui lòng nhập số điện thoại")
            return False
        
        return True
    
    def _get_user_info(self):
        """
        Lấy thông tin người dùng
        
        Returns:
            dict: Thông tin người dùng
        """
        return {
            'full_name': self.name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'address': self.address_input.text().strip(),
            'birth_date': self.birth_date_input.date().toString("dd/MM/yyyy"),
            'experience': self.experience_input.toPlainText().strip(),
            'education': self.education_input.toPlainText().strip(),
            'skills': self.skills_input.toPlainText().strip(),
            'additional_info': self.additional_info_input.toPlainText().strip(),
        }
    
    def close(self):
        """
        Đóng tab
        """
        super().close() 