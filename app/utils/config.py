"""
Configuration management for the application
Loads environment variables from .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Crawling configuration
MAX_THREADS = int(os.getenv('MAX_THREADS', 5))
TIMEOUT = int(os.getenv('TIMEOUT', 30))
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

# Job websites to crawl from
JOB_WEBSITES = [
    'VietnamWorks',
    'TopCV',
    'CareerViet',
    'JobsGO',
    'CareerLink',
    'Timviecnhanh',
    'JobStreet',
    'Glints',
    'ITviec',
    '123Job'
]

# Output file paths
JOB_LINKS_FILE = 'app/data/job_link_list.csv'
JOB_DETAILS_FILE = 'app/data/job_opportunities.csv'
CV_OUTPUT_DIR = 'app/data/cv_output'

# Create necessary directories if they don't exist
os.makedirs(os.path.dirname(JOB_LINKS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(JOB_DETAILS_FILE), exist_ok=True)
os.makedirs(CV_OUTPUT_DIR, exist_ok=True)

# Experience levels
EXPERIENCE_LEVELS = [
    'Không yêu cầu kinh nghiệm',
    'Thực tập sinh',
    'Fresher',
    'Junior',
    'Mid-level',
    'Senior',
    'Quản lý'
]

# Job types
JOB_TYPES = [
    'Toàn thời gian',
    'Bán thời gian',
    'Hợp đồng',
    'Freelance',
    'Mùa vụ/Tạm thời',
    'Thực tập'
]

# Work modes
WORK_MODES = [
    'Tại văn phòng',
    'Làm từ xa',
    'Hybrid',
    'Không xác định'
]

# Languages
LANGUAGES = [
    'Tiếng Việt',
    'Tiếng Anh',
    'Cả hai',
    'Khác'
]

# Vietnam provinces and districts
# This is a simplified list, would need to be expanded in production
VIETNAM_LOCATIONS = {
    'Hà Nội': ['Ba Đình', 'Hoàn Kiếm', 'Hai Bà Trưng', 'Đống Đa', 'Tây Hồ', 'Cầu Giấy', 'Thanh Xuân', 'Hoàng Mai'],
    'Hồ Chí Minh': ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 4', 'Quận 5', 'Quận 6', 'Quận 7', 'Quận 8', 'Quận 9', 'Quận 10', 'Quận 11', 'Quận 12', 'Bình Thạnh', 'Phú Nhuận', 'Tân Bình'],
    'Đà Nẵng': ['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Ngũ Hành Sơn', 'Liên Chiểu', 'Cẩm Lệ'],
    'Hải Phòng': ['Hồng Bàng', 'Ngô Quyền', 'Lê Chân', 'Kiến An', 'Đồ Sơn', 'Dương Kinh'],
    'Cần Thơ': ['Ninh Kiều', 'Bình Thủy', 'Cái Răng', 'Ô Môn', 'Thốt Nốt']
} 