"""
VietnamWorks crawler implementation
"""
import re
import json
from urllib.parse import urlencode
from app.crawlers.base_crawler import BaseCrawler
from app.utils.openai_helper import extract_job_info_with_openai, search_jobs_with_openai

class VietnamWorksCrawler(BaseCrawler):
    """
    Crawler cho trang web VietnamWorks
    """
    
    def __init__(self):
        """
        Khởi tạo crawler cho VietnamWorks
        """
        super().__init__("VietnamWorks")
        self.base_url = "https://www.vietnamworks.com"
        self.search_url = f"{self.base_url}/tim-kiem-viec-lam-nhanh"
    
    def search_jobs(self, keywords, location=None, filters=None):
        """
        Tìm kiếm việc làm trên VietnamWorks sử dụng OpenAI Deep Search
        
        Args:
            keywords (list): Danh sách từ khóa tìm kiếm
            location (dict, optional): Thông tin vị trí địa lý
            filters (dict, optional): Các bộ lọc bổ sung
            
        Returns:
            list: Danh sách các URL việc làm
        """
        print(f"Bắt đầu tìm kiếm thông minh với OpenAI cho từ khóa: {keywords}")
        
        # Sử dụng OpenAI để tìm kiếm việc làm phù hợp
        smart_search_urls = search_jobs_with_openai(keywords, self.base_url, location, filters)
        
        # Nếu tìm kiếm thông minh không thành công, sử dụng phương pháp tìm kiếm truyền thống
        if not smart_search_urls:
            print("Tìm kiếm thông minh không thành công, chuyển sang phương pháp truyền thống")
            return self._search_jobs_traditional(keywords, location, filters)
        
        print(f"Đã tìm thấy {len(smart_search_urls)} việc làm phù hợp qua tìm kiếm thông minh")
        return smart_search_urls
    
    def _search_jobs_traditional(self, keywords, location=None, filters=None):
        """
        Phương pháp tìm kiếm truyền thống (backup) khi phương pháp tìm kiếm thông minh thất bại
        
        Args:
            keywords (list): Danh sách từ khóa tìm kiếm
            location (dict, optional): Thông tin vị trí địa lý
            filters (dict, optional): Các bộ lọc bổ sung
            
        Returns:
            list: Danh sách các URL việc làm
        """
        job_urls = []
        
        # Xử lý từng từ khóa
        for keyword in keywords:
            # Xây dựng tham số tìm kiếm
            params = {
                'q': keyword
            }
            
            # Thêm vị trí nếu có
            if location and 'company_province' in location:
                params['province'] = location['company_province']
            
            # Thêm các bộ lọc nếu có
            if filters:
                if 'experience' in filters:
                    params['exp'] = filters['experience']
                if 'job_type' in filters:
                    params['jobtype'] = filters['job_type']
                if 'salary' in filters:
                    params['salary'] = filters['salary']
            
            # Tạo URL tìm kiếm
            search_url = f"{self.search_url}?{urlencode(params)}"
            
            # Tải trang tìm kiếm
            soup = self.get_page(search_url)
            if not soup:
                continue
            
            # Trích xuất các URL việc làm từ trang tìm kiếm
            job_links = soup.select('h3.job-title > a')
            for link in job_links:
                job_url = link.get('href')
                if job_url:
                    # Đảm bảo URL đầy đủ
                    if not job_url.startswith('http'):
                        job_url = f"{self.base_url}{job_url}"
                    job_urls.append(job_url)
        
        return job_urls
    
    def extract_job_details(self, url):
        """
        Trích xuất thông tin chi tiết từ trang việc làm VietnamWorks
        
        Args:
            url (str): URL của trang việc làm
            
        Returns:
            dict: Thông tin chi tiết về việc làm
        """
        soup = self.get_page(url)
        if not soup:
            return None
        
        # Sử dụng OpenAI để trích xuất thông tin
        html_content = str(soup)
        job_details = extract_job_info_with_openai(html_content, url)
        
        # Thêm thông tin nguồn
        job_details['source'] = self.name
        job_details['url'] = url
        
        return job_details 