"""
Base crawler class for all job website crawlers
"""
import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import time
import random
from app.utils.config import USER_AGENT, TIMEOUT

class BaseCrawler(ABC):
    """
    Lớp cơ sở cho tất cả các crawler
    """
    
    def __init__(self, name):
        """
        Khởi tạo crawler với tên và cấu hình cơ bản
        
        Args:
            name (str): Tên của trang web việc làm
        """
        self.name = name
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.timeout = TIMEOUT
    
    def get_page(self, url):
        """
        Tải nội dung trang web từ URL
        
        Args:
            url (str): URL của trang web cần tải
            
        Returns:
            BeautifulSoup: Đối tượng BeautifulSoup chứa nội dung trang
            None: Nếu có lỗi xảy ra
        """
        try:
            # Thêm độ trễ ngẫu nhiên để tránh bị chặn
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Phân tích cú pháp HTML với BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải trang {url}: {e}")
            return None
    
    @abstractmethod
    def search_jobs(self, keywords, location=None, filters=None):
        """
        Tìm kiếm việc làm dựa trên từ khóa và bộ lọc
        
        Args:
            keywords (list): Danh sách từ khóa tìm kiếm
            location (dict, optional): Thông tin vị trí địa lý
            filters (dict, optional): Các bộ lọc bổ sung
            
        Returns:
            list: Danh sách các URL việc làm
        """
        pass
    
    @abstractmethod
    def extract_job_details(self, url):
        """
        Trích xuất thông tin chi tiết từ trang việc làm
        
        Args:
            url (str): URL của trang việc làm
            
        Returns:
            dict: Thông tin chi tiết về việc làm
        """
        pass
    
    def clean_text(self, text):
        """
        Làm sạch văn bản, loại bỏ khoảng trắng thừa
        
        Args:
            text (str): Văn bản cần làm sạch
            
        Returns:
            str: Văn bản đã làm sạch
        """
        if text is None:
            return ""
        return ' '.join(text.strip().split()) 