"""
Tab tìm kiếm việc làm
"""
import os
import threading
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QCheckBox, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QProgressBar, QGroupBox, QScrollArea, QGridLayout, QDateEdit,
    QSplitter, QFrame, QTextEdit, QMessageBox, QHeaderView, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QIcon
from app.crawlers.crawler_manager import CrawlerManager
from app.utils.config import (
    EXPERIENCE_LEVELS, JOB_TYPES, WORK_MODES, LANGUAGES, VIETNAM_LOCATIONS
)

# Thiết lập logger
logger = logging.getLogger(__name__)

class JobLinkCrawlerThread(QThread):
    """
    Thread để crawl link việc làm
    """
    progress_updated = pyqtSignal(int)
    link_crawled = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def __init__(self, crawler_manager, keywords, location, filters, limit):
        super().__init__()
        self.crawler_manager = crawler_manager
        self.keywords = keywords
        self.location = location
        self.filters = filters
        self.limit = limit
    
    def run(self):
        try:
            # Thiết lập callback
            def on_link_crawled(link, source):
                self.link_crawled.emit({
                    'url': link,
                    'source': source,
                    'status': 'Đang chờ'
                })
            
            def on_progress_updated(task_type, progress):
                if task_type == 'links':
                    self.progress_updated.emit(int(progress))
            
            # Thiết lập callback cho crawler manager
            self.crawler_manager.set_callbacks(
                on_link_crawled=on_link_crawled,
                on_progress_updated=on_progress_updated
            )
            
            # Crawl link
            self.crawler_manager.crawl_job_links(
                self.keywords, self.location, self.filters, self.limit
            )
            
            # Phát tín hiệu khi hoàn thành
            self.finished_signal.emit()
        
        except Exception as e:
            self.error_signal.emit(str(e))

class JobDetailCrawlerThread(QThread):
    """
    Thread để crawl chi tiết việc làm
    """
    progress_updated = pyqtSignal(int)
    detail_crawled = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def __init__(self, crawler_manager, links=None):
        super().__init__()
        self.crawler_manager = crawler_manager
        self.links = links
    
    def run(self):
        try:
            # Thiết lập callback
            def on_detail_crawled(job_detail):
                self.detail_crawled.emit(job_detail)
            
            def on_progress_updated(task_type, progress):
                if task_type == 'details':
                    self.progress_updated.emit(int(progress))
            
            # Thiết lập callback cho crawler manager
            self.crawler_manager.set_callbacks(
                on_detail_crawled=on_detail_crawled,
                on_progress_updated=on_progress_updated
            )
            
            # Crawl chi tiết
            self.crawler_manager.crawl_job_details(self.links)
            
            # Phát tín hiệu khi hoàn thành
            self.finished_signal.emit()
        
        except Exception as e:
            self.error_signal.emit(str(e))

class JobSearchTab(QWidget):
    """
    Tab tìm kiếm việc làm
    """
    # Tín hiệu
    status_message = pyqtSignal(str)
    job_selected = pyqtSignal(dict)
    
    def __init__(self):
        """
        Khởi tạo tab tìm kiếm việc làm
        """
        super().__init__()
        
        # Khởi tạo crawler manager
        self.crawler_manager = CrawlerManager()
        
        # Biến theo dõi trạng thái
        self.link_crawling = False
        self.detail_crawling = False
        
        # Danh sách link và chi tiết
        self.job_links = []
        self.job_details = []
        
        # Thiết lập giao diện
        self.init_ui()
        
        # Kết nối các tín hiệu
        self.connect_signals()
        
        # Log
        logger.info("Tab tìm kiếm việc làm đã được khởi tạo")
    
    def init_ui(self):
        """
        Thiết lập giao diện cho tab
        """
        # Layout chính
        self.main_layout = QVBoxLayout(self)
        
        # Tạo scroll area chính bao phủ toàn bộ tab
        main_scroll_area = QScrollArea()
        main_scroll_area.setWidgetResizable(True)
        main_scroll_area.setFrameShape(QFrame.NoFrame)
        self.main_layout.addWidget(main_scroll_area)
        
        # Widget chính chứa tất cả các thành phần
        main_content_widget = QWidget()
        main_scroll_area.setWidget(main_content_widget)
        main_content_layout = QVBoxLayout(main_content_widget)
        
        # Tạo splitter để chia màn hình thành 2 phần
        self.splitter = QSplitter(Qt.Vertical)
        main_content_layout.addWidget(self.splitter)
        
        # === PHẦN 1: FORM TÌM KIẾM ===
        # Tạo scroll area cho form tìm kiếm
        search_form_scroll = QScrollArea()
        search_form_scroll.setWidgetResizable(True)
        search_form_scroll.setFrameShape(QFrame.NoFrame)
        self.splitter.addWidget(search_form_scroll)
        
        # Widget chứa nội dung form tìm kiếm
        self.search_form_widget = QWidget()
        search_form_scroll.setWidget(self.search_form_widget)
        
        # === PHẦN 2: KẾT QUẢ ===
        # Tạo scroll area cho phần kết quả
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setFrameShape(QFrame.NoFrame)
        self.splitter.addWidget(results_scroll)
        
        # Widget chứa nội dung kết quả
        self.results_widget = QWidget()
        results_scroll.setWidget(self.results_widget)
        
        # Thiết lập form tìm kiếm
        self.setup_search_form()
        
        # Thiết lập phần kết quả
        self.setup_results_section()
        
        # Thiết lập tỷ lệ phân chia
        self.splitter.setSizes([400, 600])
        
        # Đảm bảo cuộn mượt mà khi nội dung thay đổi
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)
    
    def setup_search_form(self):
        """
        Thiết lập form tìm kiếm
        """
        # Layout cho form
        form_layout = QVBoxLayout(self.search_form_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(10)
        
        # Group box Bước 1
        step1_group = QGroupBox("Bước 1: Crawl Link Tuyển Dụng")
        form_layout.addWidget(step1_group)
        
        # Layout cho Bước 1
        step1_layout = QVBoxLayout(step1_group)
        
        # Chế độ tìm kiếm
        search_mode_layout = QHBoxLayout()
        step1_layout.addLayout(search_mode_layout)
        
        search_mode_layout.addWidget(QLabel("<b>Chế độ tìm kiếm:</b>"))
        
        # Radio buttons cho chế độ tìm kiếm
        self.search_mode_group = QButtonGroup()
        self.deep_search_radio = QRadioButton("OpenAI Deep Search (Thông minh)")
        self.deep_search_radio.setChecked(True)
        self.traditional_search_radio = QRadioButton("Tìm kiếm truyền thống")
        self.search_mode_group.addButton(self.deep_search_radio)
        self.search_mode_group.addButton(self.traditional_search_radio)
        
        search_mode_layout.addWidget(self.deep_search_radio)
        search_mode_layout.addWidget(self.traditional_search_radio)
        search_mode_layout.addStretch()
        
        # Thêm tooltip giải thích
        self.deep_search_radio.setToolTip("Sử dụng OpenAI để phân tích ngữ nghĩa và tìm kiếm thông minh, hiểu ý định tìm kiếm của người dùng")
        self.traditional_search_radio.setToolTip("Tìm kiếm đơn giản bằng cách ghép từ khóa vào URL")
        
        # Grid layout cho các trường nhập liệu
        input_grid = QGridLayout()
        step1_layout.addLayout(input_grid)
        
        # Từ khóa công việc
        input_grid.addWidget(QLabel("Công việc cần tìm:"), 0, 0)
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Nhập từ khóa, phân cách bằng dấu phẩy (,)")
        input_grid.addWidget(self.keywords_input, 0, 1, 1, 3)
        
        # Thêm tooltip cho từ khóa
        self.keywords_input.setToolTip("Trong chế độ tìm kiếm thông minh, bạn có thể nhập cả câu mô tả công việc mong muốn")
        
        # Địa điểm của bạn
        input_grid.addWidget(QLabel("Địa điểm của bạn:"), 1, 0)
        
        location_layout = QHBoxLayout()
        input_grid.addLayout(location_layout, 1, 1, 1, 3)
        
        # Tỉnh/Thành phố của bạn
        location_layout.addWidget(QLabel("Tỉnh/Thành phố:"))
        self.user_province_combo = QComboBox()
        self.user_province_combo.addItems([""] + list(VIETNAM_LOCATIONS.keys()))
        location_layout.addWidget(self.user_province_combo)
        
        # Quận/Huyện của bạn
        location_layout.addWidget(QLabel("Quận/Huyện:"))
        self.user_district_combo = QComboBox()
        location_layout.addWidget(self.user_district_combo)
        
        # Địa điểm công ty
        input_grid.addWidget(QLabel("Địa điểm công ty (Nơi bạn muốn ứng tuyển):"), 2, 0)
        
        company_location_layout = QHBoxLayout()
        input_grid.addLayout(company_location_layout, 2, 1, 1, 3)
        
        # Tỉnh/Thành phố công ty
        company_location_layout.addWidget(QLabel("Tỉnh/Thành phố:"))
        self.company_province_combo = QComboBox()
        self.company_province_combo.addItems([""] + list(VIETNAM_LOCATIONS.keys()))
        company_location_layout.addWidget(self.company_province_combo)
        
        # Giới hạn link crawl
        input_grid.addWidget(QLabel("Giới hạn link crawl:"), 3, 0)
        
        limit_layout = QHBoxLayout()
        input_grid.addLayout(limit_layout, 3, 1, 1, 3)
        
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setMinimum(1)
        self.limit_spinbox.setMaximum(1000)
        self.limit_spinbox.setValue(50)
        limit_layout.addWidget(self.limit_spinbox)
        
        limit_layout.addWidget(QLabel("hoặc"))
        
        self.no_limit_checkbox = QCheckBox("Crawl đến khi hết dữ liệu")
        limit_layout.addWidget(self.no_limit_checkbox)
        limit_layout.addStretch()
        
        # Nút crawl link
        button_layout = QHBoxLayout()
        step1_layout.addLayout(button_layout)
        
        self.crawl_links_button = QPushButton("Bắt đầu Crawl Link Tuyển Dụng")
        button_layout.addWidget(self.crawl_links_button)
        
        self.pause_links_button = QPushButton("Tạm Dừng Crawl Link")
        self.pause_links_button.setEnabled(False)
        button_layout.addWidget(self.pause_links_button)
        
        # Thanh tiến trình
        step1_layout.addWidget(QLabel("Tiến trình crawl link:"))
        self.links_progress_bar = QProgressBar()
        step1_layout.addWidget(self.links_progress_bar)
        
        # Group box Bước 2
        step2_group = QGroupBox("Bước 2: Crawl Dữ Liệu Chi Tiết")
        form_layout.addWidget(step2_group)
        
        # Layout cho Bước 2
        step2_layout = QVBoxLayout(step2_group)
        
        # Nút crawl chi tiết
        button_layout2 = QHBoxLayout()
        step2_layout.addLayout(button_layout2)
        
        self.crawl_details_button = QPushButton("Bước 1 -> Bước 2: Bắt đầu Crawl Dữ Liệu Chi Tiết")
        self.crawl_details_button.setEnabled(False)
        button_layout2.addWidget(self.crawl_details_button)
        
        self.pause_details_button = QPushButton("Tạm Dừng Crawl Chi Tiết")
        self.pause_details_button.setEnabled(False)
        button_layout2.addWidget(self.pause_details_button)
        
        # Thanh tiến trình
        step2_layout.addWidget(QLabel("Tiến trình crawl chi tiết:"))
        self.details_progress_bar = QProgressBar()
        step2_layout.addWidget(self.details_progress_bar)
        
        # Group box Bước 3
        step3_group = QGroupBox("Bước 3: Xuất CSV")
        form_layout.addWidget(step3_group)
        
        # Layout cho Bước 3
        step3_layout = QVBoxLayout(step3_group)
        
        # Nút xuất CSV
        self.export_csv_button = QPushButton("Bước 2 -> Bước 3: Xuất CSV")
        self.export_csv_button.setEnabled(False)
        step3_layout.addWidget(self.export_csv_button)
        
        # Thêm khoảng cách dưới cùng
        form_layout.addStretch()
    
    def setup_results_section(self):
        """
        Thiết lập phần kết quả
        """
        # Layout cho kết quả
        results_layout = QVBoxLayout(self.results_widget)
        results_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab cho Link và Chi tiết
        self.results_tabs = QSplitter(Qt.Vertical)
        results_layout.addWidget(self.results_tabs)
        
        # Phần bảng link - thêm khả năng cuộn
        links_container = QWidget()
        self.results_tabs.addWidget(links_container)
        links_layout = QVBoxLayout(links_container)
        links_layout.setContentsMargins(0, 0, 0, 0)
        
        links_label = QLabel("<b>Bảng Link Tuyển Dụng:</b>")
        links_layout.addWidget(links_label)
        
        # Tạo scroll area cho bảng link
        links_scroll = QScrollArea()
        links_scroll.setWidgetResizable(True)
        links_scroll.setFrameShape(QFrame.NoFrame)
        links_layout.addWidget(links_scroll)
        
        # Widget chứa bảng link
        links_table_widget = QWidget()
        links_scroll.setWidget(links_table_widget)
        links_table_layout = QVBoxLayout(links_table_widget)
        links_table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bảng link
        self.links_table = QTableWidget(0, 3)
        self.links_table.setHorizontalHeaderLabels(["STT", "Link Tuyển Dụng", "Trạng thái"])
        self.links_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.links_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.links_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        links_table_layout.addWidget(self.links_table)
        
        # Phần bảng chi tiết - thêm khả năng cuộn
        details_container = QWidget()
        self.results_tabs.addWidget(details_container)
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        details_label = QLabel("<b>Bảng Dữ Liệu Chi Tiết:</b>")
        details_layout.addWidget(details_label)
        
        # Tạo scroll area cho bảng chi tiết
        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setFrameShape(QFrame.NoFrame)
        details_layout.addWidget(details_scroll)
        
        # Widget chứa bảng chi tiết
        details_table_widget = QWidget()
        details_scroll.setWidget(details_table_widget)
        details_table_layout = QVBoxLayout(details_table_widget)
        details_table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bảng chi tiết
        self.details_table = QTableWidget(0, 18)
        self.details_table.setHorizontalHeaderLabels([
            "STT", "Tiêu đề công việc", "Tên công ty", "Địa chỉ công ty", 
            "Địa điểm làm việc", "Mức lương", "Loại công việc", "Hình thức làm việc", 
            "Kỹ năng yêu cầu", "Kinh nghiệm", "Học vấn", "Mô tả công việc", 
            "Lợi ích", "Hạn nộp hồ sơ", "Ngôn ngữ", "Email liên hệ", 
            "Người liên hệ", "Khoảng cách"
        ])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Thiết lập cuộn ngang cho bảng chi tiết
        self.details_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.details_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        
        details_table_layout.addWidget(self.details_table)
        
        # Thiết lập tỷ lệ phân chia
        self.results_tabs.setSizes([300, 500])
    
    def connect_signals(self):
        """
        Kết nối các tín hiệu
        """
        # Kết nối tín hiệu cho form tìm kiếm
        self.user_province_combo.currentIndexChanged.connect(self.update_user_districts)
        self.company_province_combo.currentIndexChanged.connect(self.update_company_districts)
        self.no_limit_checkbox.stateChanged.connect(self.toggle_limit_spinbox)
        
        # Kết nối tín hiệu cho nút
        self.crawl_links_button.clicked.connect(self.start_crawl_links)
        self.pause_links_button.clicked.connect(self.toggle_pause_links)
        self.crawl_details_button.clicked.connect(self.start_crawl_details)
        self.pause_details_button.clicked.connect(self.toggle_pause_details)
        self.export_csv_button.clicked.connect(self.export_csv)
        
        # Kết nối tín hiệu cho bảng
        self.details_table.itemSelectionChanged.connect(self.on_job_selected)
        
        # Kết nối tín hiệu cho radio buttons chế độ tìm kiếm
        self.deep_search_radio.toggled.connect(self.on_search_mode_changed)
        self.traditional_search_radio.toggled.connect(self.on_search_mode_changed)
    
    def update_user_districts(self):
        """
        Cập nhật danh sách quận/huyện của người dùng khi thay đổi tỉnh/thành phố
        """
        province = self.user_province_combo.currentText()
        self.user_district_combo.clear()
        
        if province and province in VIETNAM_LOCATIONS:
            self.user_district_combo.addItems([""] + VIETNAM_LOCATIONS[province])
    
    def update_company_districts(self):
        """
        Cập nhật danh sách quận/huyện của công ty khi thay đổi tỉnh/thành phố
        """
        province = self.company_province_combo.currentText()
        
        if province and province in VIETNAM_LOCATIONS:
            # Trong trường hợp thực tế, ở đây sẽ tạo checkbox cho mỗi quận/huyện
            # Hiện tại chỉ giả lập bằng combobox
            pass
    
    def toggle_limit_spinbox(self):
        """
        Bật/tắt spinbox giới hạn link khi checkbox thay đổi
        """
        self.limit_spinbox.setEnabled(not self.no_limit_checkbox.isChecked())
    
    def on_search_mode_changed(self):
        """
        Xử lý khi người dùng thay đổi chế độ tìm kiếm
        """
        # Cập nhật chế độ tìm kiếm trong crawler manager
        use_deep_search = self.deep_search_radio.isChecked()
        self.crawler_manager.set_search_mode(use_deep_search)
        
        # Cập nhật tooltip cho ô nhập từ khóa
        if use_deep_search:
            self.keywords_input.setPlaceholderText("Nhập từ khóa, câu mô tả, phân cách bằng dấu phẩy (,)")
            self.keywords_input.setToolTip("Trong chế độ tìm kiếm thông minh, bạn có thể nhập cả câu mô tả công việc mong muốn")
            self.status_message.emit("Đã chuyển sang chế độ tìm kiếm thông minh với OpenAI Deep Search")
        else:
            self.keywords_input.setPlaceholderText("Nhập từ khóa, phân cách bằng dấu phẩy (,)")
            self.keywords_input.setToolTip("Nhập từ khóa chính xác để tìm kiếm")
            self.status_message.emit("Đã chuyển sang chế độ tìm kiếm truyền thống")
    
    def start_crawl_links(self):
        """
        Bắt đầu crawl link
        """
        # Kiểm tra từ khóa
        keywords_text = self.keywords_input.text().strip()
        if not keywords_text:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ít nhất một từ khóa tìm kiếm!")
            return
        
        # Phân tách từ khóa
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        
        # Thiết lập location
        location = {}
        if self.user_province_combo.currentText():
            location['user_province'] = self.user_province_combo.currentText()
            if self.user_district_combo.currentText():
                location['user_district'] = self.user_district_combo.currentText()
        
        if self.company_province_combo.currentText():
            location['company_province'] = self.company_province_combo.currentText()
            # Trong trường hợp thực tế, sẽ lấy danh sách quận/huyện được chọn từ checkbox
        
        # Thiết lập giới hạn
        limit = None if self.no_limit_checkbox.isChecked() else self.limit_spinbox.value()
        
        # Thiết lập filters (trong trường hợp thực tế sẽ lấy từ các trường khác)
        filters = {}
        
        # Xóa dữ liệu cũ
        self.job_links = []
        self.links_table.setRowCount(0)
        self.links_progress_bar.setValue(0)
        
        # Ghi log
        logger.info(f"Bắt đầu crawl link với từ khóa: {keywords}")
        logger.info(f"Chế độ tìm kiếm: {'OpenAI Deep Search' if self.deep_search_radio.isChecked() else 'Tìm kiếm truyền thống'}")
        
        # Cập nhật trạng thái
        self.link_crawling = True
        self.crawl_links_button.setEnabled(False)
        self.pause_links_button.setEnabled(True)
        self.pause_links_button.setText("Tạm Dừng Crawl Link")
        
        # Phát tín hiệu trạng thái
        mode_text = "thông minh (OpenAI Deep Search)" if self.deep_search_radio.isChecked() else "truyền thống"
        self.status_message.emit(f"Đang crawl link tuyển dụng với chế độ tìm kiếm {mode_text}...")
        
        # Tạo thread để crawl
        self.link_crawler_thread = JobLinkCrawlerThread(
            self.crawler_manager, keywords, location, filters, limit
        )
        
        # Kết nối tín hiệu
        self.link_crawler_thread.progress_updated.connect(self.update_links_progress)
        self.link_crawler_thread.link_crawled.connect(self.add_link_to_table)
        self.link_crawler_thread.finished_signal.connect(self.on_links_crawl_finished)
        self.link_crawler_thread.error_signal.connect(self.on_crawl_error)
        
        # Bắt đầu thread
        self.link_crawler_thread.start()
    
    def toggle_pause_links(self):
        """
        Tạm dừng/tiếp tục crawl link
        """
        if not self.link_crawling:
            return
        
        if self.crawler_manager.pause_flag.is_set():
            # Tạm dừng
            self.crawler_manager.pause_crawling()
            self.pause_links_button.setText("Tiếp Tục Crawl Link")
            self.status_message.emit("Đã tạm dừng crawl link tuyển dụng")
        else:
            # Tiếp tục
            self.crawler_manager.resume_crawling()
            self.pause_links_button.setText("Tạm Dừng Crawl Link")
            self.status_message.emit("Đang crawl link tuyển dụng...")
    
    def update_links_progress(self, value):
        """
        Cập nhật thanh tiến trình crawl link
        
        Args:
            value (int): Giá trị phần trăm tiến trình
        """
        self.links_progress_bar.setValue(value)
    
    def add_link_to_table(self, link_info):
        """
        Thêm link vào bảng
        
        Args:
            link_info (dict): Thông tin về link
        """
        # Thêm vào danh sách
        self.job_links.append(link_info)
        
        # Thêm vào bảng
        row = self.links_table.rowCount()
        self.links_table.insertRow(row)
        
        # STT
        self.links_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        
        # Link
        self.links_table.setItem(row, 1, QTableWidgetItem(link_info['url']))
        
        # Trạng thái
        self.links_table.setItem(row, 2, QTableWidgetItem(link_info['status']))
    
    def on_links_crawl_finished(self):
        """
        Xử lý khi crawl link hoàn thành
        """
        # Cập nhật trạng thái
        self.link_crawling = False
        self.crawl_links_button.setEnabled(True)
        self.pause_links_button.setEnabled(False)
        self.crawl_details_button.setEnabled(True)
        
        # Cập nhật thanh tiến trình
        self.links_progress_bar.setValue(100)
        
        # Phát tín hiệu trạng thái
        self.status_message.emit(f"Đã crawl xong {len(self.job_links)} link tuyển dụng")
        
        # Hiển thị thông báo
        QMessageBox.information(
            self, "Hoàn thành", 
            f"Đã crawl xong {len(self.job_links)} link tuyển dụng.\n"
            "Nhấn 'Bước 1 -> Bước 2: Bắt đầu Crawl Dữ Liệu Chi Tiết' để tiếp tục."
        )
    
    def start_crawl_details(self):
        """
        Bắt đầu crawl chi tiết
        """
        if not self.job_links:
            QMessageBox.warning(self, "Cảnh báo", "Không có link tuyển dụng để crawl chi tiết!")
            return
        
        # Xóa dữ liệu cũ
        self.job_details = []
        self.details_table.setRowCount(0)
        self.details_progress_bar.setValue(0)
        
        # Cập nhật trạng thái
        self.detail_crawling = True
        self.crawl_details_button.setEnabled(False)
        self.pause_details_button.setEnabled(True)
        self.pause_details_button.setText("Tạm Dừng Crawl Chi Tiết")
        
        # Phát tín hiệu trạng thái
        self.status_message.emit("Đang crawl dữ liệu chi tiết...")
        
        # Tạo thread để crawl
        self.detail_crawler_thread = JobDetailCrawlerThread(
            self.crawler_manager, self.job_links
        )
        
        # Kết nối tín hiệu
        self.detail_crawler_thread.progress_updated.connect(self.update_details_progress)
        self.detail_crawler_thread.detail_crawled.connect(self.add_detail_to_table)
        self.detail_crawler_thread.finished_signal.connect(self.on_details_crawl_finished)
        self.detail_crawler_thread.error_signal.connect(self.on_crawl_error)
        
        # Bắt đầu thread
        self.detail_crawler_thread.start()
    
    def toggle_pause_details(self):
        """
        Tạm dừng/tiếp tục crawl chi tiết
        """
        if not self.detail_crawling:
            return
        
        if self.crawler_manager.pause_flag.is_set():
            # Tạm dừng
            self.crawler_manager.pause_crawling()
            self.pause_details_button.setText("Tiếp Tục Crawl Chi Tiết")
            self.status_message.emit("Đã tạm dừng crawl dữ liệu chi tiết")
        else:
            # Tiếp tục
            self.crawler_manager.resume_crawling()
            self.pause_details_button.setText("Tạm Dừng Crawl Chi Tiết")
            self.status_message.emit("Đang crawl dữ liệu chi tiết...")
    
    def update_details_progress(self, value):
        """
        Cập nhật thanh tiến trình crawl chi tiết
        
        Args:
            value (int): Giá trị phần trăm tiến trình
        """
        self.details_progress_bar.setValue(value)
    
    def add_detail_to_table(self, job_detail):
        """
        Thêm chi tiết vào bảng
        
        Args:
            job_detail (dict): Thông tin chi tiết về việc làm
        """
        # Thêm vào danh sách
        self.job_details.append(job_detail)
        
        # Thêm vào bảng
        row = self.details_table.rowCount()
        self.details_table.insertRow(row)
        
        # STT
        self.details_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        
        # Thiết lập các cột
        columns = [
            "job_title", "company_name", "company_address", "job_location",
            "salary_range", "job_type", "work_mode", "required_skills",
            "experience_level", "education_requirements", "brief_job_description",
            "job_benefits", "application_deadline", "language_requirement",
            "contact_email", "contact_person", "distance"
        ]
        
        for i, column in enumerate(columns):
            value = job_detail.get(column, "")
            if isinstance(value, (list, tuple)):
                value = ", ".join(map(str, value))
            self.details_table.setItem(row, i + 1, QTableWidgetItem(str(value)))
    
    def on_details_crawl_finished(self):
        """
        Xử lý khi crawl chi tiết hoàn thành
        """
        # Cập nhật trạng thái
        self.detail_crawling = False
        self.crawl_details_button.setEnabled(True)
        self.pause_details_button.setEnabled(False)
        self.export_csv_button.setEnabled(True)
        
        # Cập nhật thanh tiến trình
        self.details_progress_bar.setValue(100)
        
        # Phát tín hiệu trạng thái
        self.status_message.emit(f"Đã crawl xong {len(self.job_details)} chi tiết việc làm")
        
        # Hiển thị thông báo
        QMessageBox.information(
            self, "Hoàn thành", 
            f"Đã crawl xong {len(self.job_details)} chi tiết việc làm.\n"
            "Nhấn 'Bước 2 -> Bước 3: Xuất CSV' để lưu kết quả."
        )
    
    def on_crawl_error(self, error_message):
        """
        Xử lý khi có lỗi trong quá trình crawl
        
        Args:
            error_message (str): Thông báo lỗi
        """
        # Kiểm tra xem có phải lỗi OpenAI API không
        is_openai_error = False
        openai_error_details = ""
        
        if "openai" in error_message.lower():
            is_openai_error = True
            # Trích xuất thông tin chi tiết
            if "response_format" in error_message.lower():
                openai_error_details = (
                    "\n\nLỗi này có thể do OpenAI API không hỗ trợ định dạng JSON cho mô hình được chọn. "
                    "Hãy thử chuyển sang chế độ tìm kiếm truyền thống hoặc kiểm tra lại API key của bạn."
                )
            elif "api key" in error_message.lower():
                openai_error_details = (
                    "\n\nLỗi này có thể do API key không hợp lệ hoặc đã hết hạn. "
                    "Vui lòng kiểm tra lại API key trong file .env của bạn."
                )
            elif "rate limit" in error_message.lower():
                openai_error_details = (
                    "\n\nLỗi này do bạn đã vượt quá giới hạn số lượng yêu cầu cho phép của OpenAI. "
                    "Vui lòng thử lại sau ít phút hoặc chuyển sang chế độ tìm kiếm truyền thống."
                )
            else:
                openai_error_details = (
                    "\n\nĐây là lỗi liên quan đến OpenAI API. "
                    "Vui lòng thử lại sau hoặc chuyển sang chế độ tìm kiếm truyền thống."
                )
        
        # Tạo thông báo lỗi chi tiết
        error_message_with_details = f"Đã xảy ra lỗi: {error_message}{openai_error_details}"
        
        # Hiển thị thông báo lỗi
        if is_openai_error:
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Lỗi OpenAI API")
            error_box.setText("Lỗi khi sử dụng OpenAI API")
            error_box.setInformativeText(error_message)
            error_box.setDetailedText(error_message_with_details)
            
            # Thêm nút chuyển đổi chế độ tìm kiếm
            switch_button = error_box.addButton("Chuyển sang tìm kiếm truyền thống", QMessageBox.ActionRole)
            close_button = error_box.addButton(QMessageBox.Close)
            
            error_box.exec_()
            
            if error_box.clickedButton() == switch_button:
                # Chuyển sang chế độ tìm kiếm truyền thống
                self.traditional_search_radio.setChecked(True)
                self.on_search_mode_changed()
                QMessageBox.information(self, "Thông báo", "Đã chuyển sang chế độ tìm kiếm truyền thống")
        else:
            QMessageBox.critical(self, "Lỗi", error_message_with_details)
        
        # Cập nhật trạng thái
        if self.link_crawling:
            self.link_crawling = False
            self.crawl_links_button.setEnabled(True)
            self.pause_links_button.setEnabled(False)
        
        if self.detail_crawling:
            self.detail_crawling = False
            self.crawl_details_button.setEnabled(True)
            self.pause_details_button.setEnabled(False)
        
        # Phát tín hiệu trạng thái
        self.status_message.emit(f"Lỗi: {error_message}")
        logger.error(f"Lỗi trong quá trình crawl: {error_message}")
    
    def export_csv(self):
        """
        Xuất dữ liệu chi tiết ra file CSV
        """
        if not self.job_details:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu chi tiết để xuất!")
            return
        
        # Xuất CSV
        self.crawler_manager._save_details_to_csv()
        
        # Hiển thị thông báo
        QMessageBox.information(
            self, "Xuất CSV", 
            "Đã xuất dữ liệu chi tiết ra file CSV thành công!"
        )
        
        # Phát tín hiệu trạng thái
        self.status_message.emit("Đã xuất dữ liệu chi tiết ra file CSV")
    
    def on_job_selected(self):
        """
        Xử lý khi người dùng chọn một việc làm trong bảng chi tiết
        """
        selected_items = self.details_table.selectedItems()
        if not selected_items:
            return
        
        # Lấy dòng được chọn
        row = selected_items[0].row()
        
        if row < len(self.job_details):
            # Phát tín hiệu với thông tin việc làm được chọn
            self.job_selected.emit(self.job_details[row])
