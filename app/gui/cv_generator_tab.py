"""
Tab tạo CV tự động
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QCheckBox, QTextEdit, QPushButton, QGroupBox, QScrollArea, QGridLayout,
    QFileDialog, QMessageBox, QDateEdit, QSpinBox, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon
from app.cv_generator.cv_generator import CVGenerator
from app.utils.config import (
    EXPERIENCE_LEVELS, JOB_TYPES, WORK_MODES, LANGUAGES, CV_OUTPUT_DIR
)

class CVGenerationThread(QThread):
    """
    Thread để tạo CV
    """
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, cv_generator, user_info, job_info, output_format, filename):
        super().__init__()
        self.cv_generator = cv_generator
        self.user_info = user_info
        self.job_info = job_info
        self.output_format = output_format
        self.filename = filename
    
    def run(self):
        try:
            # Tạo nội dung CV
            cv_content = self.cv_generator.generate_cv_content(self.user_info, self.job_info)
            
            # Tạo file theo định dạng
            if self.output_format == 'docx':
                output_path = self.cv_generator.generate_docx(cv_content, self.filename)
            elif self.output_format == 'pdf':
                output_path = self.cv_generator.generate_pdf(cv_content, self.filename)
            else:
                raise ValueError(f"Định dạng không hỗ trợ: {self.output_format}")
            
            # Phát tín hiệu khi hoàn thành
            self.finished_signal.emit(output_path)
        
        except Exception as e:
            self.error_signal.emit(str(e))

class CVGeneratorTab(QWidget):
    """
    Tab tạo CV tự động
    """
    # Tín hiệu
    status_message = pyqtSignal(str)
    
    def __init__(self):
        """
        Khởi tạo tab tạo CV tự động
        """
        super().__init__()
        
        # Khởi tạo CV Generator
        self.cv_generator = CVGenerator()
        
        # Thông tin công việc từ tab tìm kiếm
        self.job_info = None
        
        # Đang tạo CV hay không
        self.generating_cv = False
        
        # Thiết lập giao diện
        self.init_ui()
        
        # Kết nối các tín hiệu
        self.connect_signals()
    
    def init_ui(self):
        """
        Thiết lập giao diện cho tab
        """
        # Layout chính
        self.main_layout = QVBoxLayout(self)
        
        # Tạo splitter để chia màn hình thành 2 phần
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Phần 1: Form nhập thông tin
        self.form_widget = QWidget()
        self.splitter.addWidget(self.form_widget)
        
        # Phần 2: Xem trước CV
        self.preview_widget = QWidget()
        self.splitter.addWidget(self.preview_widget)
        
        # Thiết lập form nhập thông tin
        self.setup_form()
        
        # Thiết lập phần xem trước
        self.setup_preview()
        
        # Thiết lập tỷ lệ phân chia
        self.splitter.setSizes([600, 600])
    
    def setup_form(self):
        """
        Thiết lập form nhập thông tin
        """
        # Layout cho form
        form_layout = QVBoxLayout(self.form_widget)
        
        # Tạo scroll area để cuộn khi form dài
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        form_layout.addWidget(scroll_area)
        
        # Widget chứa nội dung form
        form_content = QWidget()
        scroll_area.setWidget(form_content)
        
        # Layout cho nội dung form
        content_layout = QVBoxLayout(form_content)
        
        # Group box thông tin cá nhân
        personal_group = QGroupBox("Thông Tin Cá Nhân")
        content_layout.addWidget(personal_group)
        
        # Layout cho thông tin cá nhân
        personal_layout = QGridLayout(personal_group)
        
        # Họ tên
        personal_layout.addWidget(QLabel("Họ và tên:"), 0, 0)
        self.full_name_input = QLineEdit()
        personal_layout.addWidget(self.full_name_input, 0, 1)
        
        # Ngày sinh
        personal_layout.addWidget(QLabel("Ngày sinh:"), 1, 0)
        self.dob_input = QDateEdit()
        self.dob_input.setDisplayFormat("dd/MM/yyyy")
        self.dob_input.setDate(QDate.currentDate().addYears(-25))  # Mặc định 25 tuổi
        personal_layout.addWidget(self.dob_input, 1, 1)
        
        # Email
        personal_layout.addWidget(QLabel("Email:"), 2, 0)
        self.email_input = QLineEdit()
        personal_layout.addWidget(self.email_input, 2, 1)
        
        # Số điện thoại
        personal_layout.addWidget(QLabel("Số điện thoại:"), 3, 0)
        self.phone_input = QLineEdit()
        personal_layout.addWidget(self.phone_input, 3, 1)
        
        # Địa chỉ
        personal_layout.addWidget(QLabel("Địa chỉ:"), 4, 0)
        self.address_input = QLineEdit()
        personal_layout.addWidget(self.address_input, 4, 1)
        
        # Group box học vấn
        education_group = QGroupBox("Học Vấn")
        content_layout.addWidget(education_group)
        
        # Layout cho học vấn
        education_layout = QGridLayout(education_group)
        
        # Trường học
        education_layout.addWidget(QLabel("Trường:"), 0, 0)
        self.school_input = QLineEdit()
        education_layout.addWidget(self.school_input, 0, 1)
        
        # Chuyên ngành
        education_layout.addWidget(QLabel("Chuyên ngành:"), 1, 0)
        self.major_input = QLineEdit()
        education_layout.addWidget(self.major_input, 1, 1)
        
        # Năm tốt nghiệp
        education_layout.addWidget(QLabel("Năm tốt nghiệp:"), 2, 0)
        self.graduation_year_input = QComboBox()
        current_year = QDate.currentDate().year()
        self.graduation_year_input.addItems([str(year) for year in range(current_year - 20, current_year + 6)])
        education_layout.addWidget(self.graduation_year_input, 2, 1)
        
        # Xếp loại
        education_layout.addWidget(QLabel("Xếp loại:"), 3, 0)
        self.grade_input = QComboBox()
        self.grade_input.addItems(["", "Xuất sắc", "Giỏi", "Khá", "Trung bình khá", "Trung bình"])
        education_layout.addWidget(self.grade_input, 3, 1)
        
        # Group box kinh nghiệm làm việc
        experience_group = QGroupBox("Kinh Nghiệm Làm Việc")
        content_layout.addWidget(experience_group)
        
        # Layout cho kinh nghiệm
        experience_layout = QVBoxLayout(experience_group)
        
        # Kinh nghiệm làm việc (textarea để người dùng nhập nhiều kinh nghiệm)
        experience_layout.addWidget(QLabel("Liệt kê kinh nghiệm làm việc (mỗi kinh nghiệm một dòng, định dạng: Công ty - Vị trí - Thời gian):"))
        self.experience_input = QTextEdit()
        self.experience_input.setPlaceholderText("Ví dụ:\nCông ty ABC - Lập trình viên Frontend - 2018-2020\nCông ty XYZ - Lập trình viên FullStack - 2020-2022")
        experience_layout.addWidget(self.experience_input)
        
        # Group box kỹ năng
        skills_group = QGroupBox("Kỹ Năng")
        content_layout.addWidget(skills_group)
        
        # Layout cho kỹ năng
        skills_layout = QVBoxLayout(skills_group)
        
        # Kỹ năng (textarea để người dùng nhập nhiều kỹ năng)
        skills_layout.addWidget(QLabel("Liệt kê các kỹ năng (mỗi kỹ năng một dòng, có thể thêm mức độ thành thạo):"))
        self.skills_input = QTextEdit()
        self.skills_input.setPlaceholderText("Ví dụ:\nJavaScript - Thành thạo\nReact - Khá\nNode.js - Cơ bản")
        skills_layout.addWidget(self.skills_input)
        
        # Group box chứng chỉ
        certificate_group = QGroupBox("Chứng Chỉ")
        content_layout.addWidget(certificate_group)
        
        # Layout cho chứng chỉ
        certificate_layout = QVBoxLayout(certificate_group)
        
        # Chứng chỉ (textarea để người dùng nhập nhiều chứng chỉ)
        certificate_layout.addWidget(QLabel("Liệt kê các chứng chỉ (mỗi chứng chỉ một dòng):"))
        self.certificates_input = QTextEdit()
        self.certificates_input.setPlaceholderText("Ví dụ:\nTOEIC 750 - 2020\nAWS Certified Developer - 2021")
        certificate_layout.addWidget(self.certificates_input)
        
        # Group box thông tin bổ sung
        additional_group = QGroupBox("Thông Tin Bổ Sung")
        content_layout.addWidget(additional_group)
        
        # Layout cho thông tin bổ sung
        additional_layout = QVBoxLayout(additional_group)
        
        # Sở thích
        additional_layout.addWidget(QLabel("Sở thích:"))
        self.hobbies_input = QTextEdit()
        self.hobbies_input.setPlaceholderText("Ví dụ:\nĐọc sách\nDu lịch\nChơi thể thao")
        additional_layout.addWidget(self.hobbies_input)
        
        # Mục tiêu nghề nghiệp
        additional_layout.addWidget(QLabel("Mục tiêu nghề nghiệp:"))
        self.career_goal_input = QTextEdit()
        self.career_goal_input.setPlaceholderText("Mô tả mục tiêu nghề nghiệp của bạn trong ngắn hạn và dài hạn")
        additional_layout.addWidget(self.career_goal_input)
        
        # Group box xuất CV
        export_group = QGroupBox("Xuất CV")
        content_layout.addWidget(export_group)
        
        # Layout cho xuất CV
        export_layout = QVBoxLayout(export_group)
        
        # Layout cho tên file và định dạng
        file_layout = QHBoxLayout()
        export_layout.addLayout(file_layout)
        
        # Tên file
        file_layout.addWidget(QLabel("Tên file:"))
        self.filename_input = QLineEdit("my_cv")
        file_layout.addWidget(self.filename_input)
        
        # Định dạng
        file_layout.addWidget(QLabel("Định dạng:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["docx", "pdf"])
        file_layout.addWidget(self.format_combo)
        
        # Nút tạo CV
        self.generate_button = QPushButton("Tạo CV")
        export_layout.addWidget(self.generate_button)
        
        # Thêm stretch để các group box không bị giãn quá to
        content_layout.addStretch()
    
    def setup_preview(self):
        """
        Thiết lập phần xem trước CV
        """
        # Layout cho phần xem trước
        preview_layout = QVBoxLayout(self.preview_widget)
        
        # Label tiêu đề
        preview_layout.addWidget(QLabel("<b>Xem Trước CV:</b>"))
        
        # TextEdit để hiển thị nội dung CV
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        # Thông tin công việc đang ứng tuyển
        job_info_group = QGroupBox("Thông Tin Công Việc Đang Ứng Tuyển")
        preview_layout.addWidget(job_info_group)
        
        job_info_layout = QVBoxLayout(job_info_group)
        
        # TextEdit để hiển thị thông tin công việc
        self.job_info_text = QTextEdit()
        self.job_info_text.setReadOnly(True)
        job_info_layout.addWidget(self.job_info_text)
        
        # Nút để mở file CV đã tạo
        self.open_cv_button = QPushButton("Mở File CV Đã Tạo")
        self.open_cv_button.setEnabled(False)
        preview_layout.addWidget(self.open_cv_button)
    
    def connect_signals(self):
        """
        Kết nối các tín hiệu
        """
        # Kết nối tín hiệu cho nút tạo CV
        self.generate_button.clicked.connect(self.generate_cv)
        
        # Kết nối tín hiệu cho nút mở file CV
        self.open_cv_button.clicked.connect(self.open_cv_file)
    
    def set_job_info(self, job_info):
        """
        Thiết lập thông tin công việc từ tab tìm kiếm việc làm
        
        Args:
            job_info (dict): Thông tin công việc
        """
        self.job_info = job_info
        
        # Hiển thị thông tin công việc
        if job_info:
            job_info_text = f"Tiêu đề: {job_info.get('job_title', '')}\n"
            job_info_text += f"Công ty: {job_info.get('company_name', '')}\n"
            job_info_text += f"Địa điểm: {job_info.get('job_location', '')}\n"
            job_info_text += f"Mức lương: {job_info.get('salary_range', '')}\n"
            job_info_text += f"Loại công việc: {job_info.get('job_type', '')}\n"
            job_info_text += f"Hình thức làm việc: {job_info.get('work_mode', '')}\n"
            job_info_text += f"Kỹ năng yêu cầu: {job_info.get('required_skills', '')}\n"
            job_info_text += f"Kinh nghiệm: {job_info.get('experience_level', '')}\n"
            job_info_text += f"Học vấn: {job_info.get('education_requirements', '')}\n"
            job_info_text += f"Mô tả: {job_info.get('brief_job_description', '')}\n"
            
            self.job_info_text.setText(job_info_text)
            
            # Phát tín hiệu trạng thái
            self.status_message.emit("Đã chọn công việc để ứng tuyển")
    
    def generate_cv(self):
        """
        Tạo CV từ thông tin người dùng nhập
        """
        # Kiểm tra thông tin cơ bản
        if not self.full_name_input.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập họ và tên!")
            return
        
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập email!")
            return
        
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số điện thoại!")
            return
        
        # Thu thập thông tin người dùng
        user_info = {
            "full_name": self.full_name_input.text().strip(),
            "dob": self.dob_input.date().toString("dd/MM/yyyy"),
            "email": self.email_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "address": self.address_input.text().strip(),
            "education": {
                "school": self.school_input.text().strip(),
                "major": self.major_input.text().strip(),
                "graduation_year": self.graduation_year_input.currentText(),
                "grade": self.grade_input.currentText()
            },
            "experience": self.experience_input.toPlainText().strip(),
            "skills": self.skills_input.toPlainText().strip(),
            "certificates": self.certificates_input.toPlainText().strip(),
            "hobbies": self.hobbies_input.toPlainText().strip(),
            "career_goal": self.career_goal_input.toPlainText().strip()
        }
        
        # Nếu không có thông tin công việc, sử dụng giá trị mặc định
        if not self.job_info:
            self.job_info = {
                "job_title": "Chưa chọn công việc",
                "company_name": "",
                "job_location": "",
                "salary_range": "",
                "job_type": "",
                "work_mode": "",
                "required_skills": "",
                "experience_level": "",
                "education_requirements": "",
                "brief_job_description": ""
            }
        
        # Lấy tên file và định dạng
        filename = self.filename_input.text().strip()
        if not filename:
            filename = "my_cv"
        
        output_format = self.format_combo.currentText()
        
        # Cập nhật trạng thái
        self.generating_cv = True
        self.generate_button.setEnabled(False)
        self.status_message.emit("Đang tạo CV...")
        
        # Tạo thread để tạo CV
        self.cv_thread = CVGenerationThread(
            self.cv_generator, user_info, self.job_info, output_format, filename
        )
        
        # Kết nối tín hiệu
        self.cv_thread.finished_signal.connect(self.on_cv_generation_finished)
        self.cv_thread.error_signal.connect(self.on_cv_generation_error)
        
        # Bắt đầu thread
        self.cv_thread.start()
    
    def on_cv_generation_finished(self, output_path):
        """
        Xử lý khi tạo CV hoàn thành
        
        Args:
            output_path (str): Đường dẫn đến file CV đã tạo
        """
        # Cập nhật trạng thái
        self.generating_cv = False
        self.generate_button.setEnabled(True)
        self.open_cv_button.setEnabled(True)
        
        # Lưu đường dẫn file CV
        self.cv_file_path = output_path
        
        # Hiển thị xem trước (nên là nội dung từ CVGenerator.generate_cv_content)
        cv_content = self.cv_generator.generate_cv_content(
            {
                "full_name": self.full_name_input.text().strip(),
                "email": self.email_input.text().strip(),
                # Thêm các thông tin khác nếu cần
            },
            self.job_info
        )
        self.preview_text.setText(cv_content)
        
        # Phát tín hiệu trạng thái
        self.status_message.emit(f"Đã tạo CV thành công và lưu tại: {output_path}")
        
        # Hiển thị thông báo
        QMessageBox.information(
            self, "Hoàn thành", 
            f"Đã tạo CV thành công!\nFile đã được lưu tại: {output_path}"
        )
    
    def on_cv_generation_error(self, error_message):
        """
        Xử lý khi có lỗi trong quá trình tạo CV
        
        Args:
            error_message (str): Thông báo lỗi
        """
        # Cập nhật trạng thái
        self.generating_cv = False
        self.generate_button.setEnabled(True)
        
        # Hiển thị thông báo lỗi
        QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi khi tạo CV: {error_message}")
        
        # Phát tín hiệu trạng thái
        self.status_message.emit(f"Lỗi khi tạo CV: {error_message}")
    
    def open_cv_file(self):
        """
        Mở file CV đã tạo
        """
        if hasattr(self, 'cv_file_path') and os.path.exists(self.cv_file_path):
            # Mở file với ứng dụng mặc định của hệ thống
            import subprocess
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.cv_file_path)
                elif os.name == 'posix':  # macOS, Linux
                    subprocess.run(['xdg-open', self.cv_file_path], check=True)
            except Exception as e:
                QMessageBox.warning(self, "Cảnh báo", f"Không thể mở file: {str(e)}")
        else:
            QMessageBox.warning(self, "Cảnh báo", "Chưa có file CV nào được tạo hoặc file đã bị xóa!") 