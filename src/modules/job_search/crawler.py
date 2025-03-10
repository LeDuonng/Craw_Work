#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module crawl dữ liệu từ các trang tuyển dụng
"""

import os
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from src.utils.config import JOB_SITES, JOB_LINK_FILE, JOB_DATA_FILE
from src.utils.logger import get_logger
from src.utils.helper import clean_text, extract_salary, save_to_csv, load_from_csv

# Khởi tạo logger
logger = get_logger()

class JobCrawler:
    """
    Class crawl dữ liệu từ các trang tuyển dụng
    """
    
    def __init__(self, use_selenium=True):
        """
        Khởi tạo crawler
        
        Args:
            use_selenium (bool): Sử dụng Selenium hay không
        """
        self.use_selenium = use_selenium
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })
        
        # Khởi tạo Selenium nếu cần
        if self.use_selenium:
            self._init_selenium()
    
    def _init_selenium(self):
        """
        Khởi tạo Selenium WebDriver
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Đã khởi tạo Selenium WebDriver")
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo Selenium WebDriver: {e}")
            self.use_selenium = False
    
    def close(self):
        """
        Đóng crawler
        """
        if self.driver:
            self.driver.quit()
            logger.info("Đã đóng Selenium WebDriver")
    
    def crawl_job_links(self, keyword, max_pages=5, sites=None):
        """
        Crawl danh sách link tuyển dụng
        
        Args:
            keyword (str): Từ khóa tìm kiếm
            max_pages (int): Số trang tối đa cần crawl
            sites (list): Danh sách các trang cần crawl
        
        Returns:
            list: Danh sách link tuyển dụng
        """
        job_links = []
        
        # Nếu không chỉ định trang, crawl tất cả
        if not sites:
            sites = list(JOB_SITES.keys())
        
        # Crawl từng trang
        for site_key in sites:
            if site_key not in JOB_SITES:
                logger.warning(f"Trang {site_key} không được hỗ trợ")
                continue
            
            site = JOB_SITES[site_key]
            logger.info(f"Đang crawl trang {site['name']}...")
            
            # Crawl từng trang
            for page in range(1, max_pages + 1):
                try:
                    # Tạo URL tìm kiếm
                    search_url = site['search_url'].format(keyword, page)
                    
                    # Crawl trang
                    if self.use_selenium:
                        links = self._crawl_page_selenium(search_url, site_key)
                    else:
                        links = self._crawl_page_requests(search_url, site_key)
                    
                    # Thêm vào danh sách
                    if links:
                        job_links.extend(links)
                        logger.info(f"Đã crawl được {len(links)} link từ trang {page} của {site['name']}")
                    else:
                        logger.warning(f"Không tìm thấy link nào từ trang {page} của {site['name']}")
                        break
                    
                    # Delay để tránh bị chặn
                    time.sleep(random.uniform(1, 3))
                except Exception as e:
                    logger.error(f"Lỗi khi crawl trang {page} của {site['name']}: {e}")
                    continue
        
        # Lưu danh sách link vào file
        if job_links:
            # Tạo dữ liệu để lưu
            data = []
            for link in job_links:
                data.append({
                    'url': link['url'],
                    'title': link['title'],
                    'company': link['company'],
                    'site': link['site'],
                })
            
            # Lưu vào file
            save_to_csv(data, JOB_LINK_FILE)
            logger.info(f"Đã lưu {len(job_links)} link vào file {JOB_LINK_FILE}")
        
        return job_links
    
    def _crawl_page_selenium(self, url, site_key):
        """
        Crawl trang bằng Selenium
        
        Args:
            url (str): URL cần crawl
            site_key (str): Khóa của trang
        
        Returns:
            list: Danh sách link tuyển dụng
        """
        if not self.driver:
            logger.error("Selenium WebDriver chưa được khởi tạo")
            return []
        
        try:
            # Truy cập URL
            self.driver.get(url)
            
            # Đợi trang load xong
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Lấy HTML
            html = self.driver.page_source
            
            # Parse HTML
            return self._parse_job_links(html, site_key)
        except Exception as e:
            logger.error(f"Lỗi khi crawl trang {url} bằng Selenium: {e}")
            return []
    
    def _crawl_page_requests(self, url, site_key):
        """
        Crawl trang bằng Requests
        
        Args:
            url (str): URL cần crawl
            site_key (str): Khóa của trang
        
        Returns:
            list: Danh sách link tuyển dụng
        """
        try:
            # Gửi request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            return self._parse_job_links(response.text, site_key)
        except Exception as e:
            logger.error(f"Lỗi khi crawl trang {url} bằng Requests: {e}")
            return []
    
    def _parse_job_links(self, html, site_key):
        """
        Parse HTML để lấy danh sách link tuyển dụng
        
        Args:
            html (str): HTML cần parse
            site_key (str): Khóa của trang
        
        Returns:
            list: Danh sách link tuyển dụng
        """
        links = []
        site = JOB_SITES[site_key]
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'lxml')
            
            # Tùy theo từng trang mà có cách parse khác nhau
            if site_key == 'vietnamworks':
                job_items = soup.select('.job-item')
                for item in job_items:
                    link_elem = item.select_one('a.job-title')
                    company_elem = item.select_one('.company-name')
                    
                    if link_elem and company_elem:
                        url = link_elem.get('href')
                        if not url.startswith('http'):
                            url = site['url'] + url
                        
                        links.append({
                            'url': url,
                            'title': clean_text(link_elem.text),
                            'company': clean_text(company_elem.text),
                            'site': site['name'],
                        })
            
            elif site_key == 'topcv':
                job_items = soup.select('.job-item')
                for item in job_items:
                    link_elem = item.select_one('h3.job-title a')
                    company_elem = item.select_one('.company-name')
                    
                    if link_elem and company_elem:
                        url = link_elem.get('href')
                        if not url.startswith('http'):
                            url = site['url'] + url
                        
                        links.append({
                            'url': url,
                            'title': clean_text(link_elem.text),
                            'company': clean_text(company_elem.text),
                            'site': site['name'],
                        })
            
            # Thêm các trang khác tương tự...
            # Đây chỉ là ví dụ, cần cập nhật cho từng trang cụ thể
            
            else:
                # Mặc định tìm các thẻ a có chứa từ "job" hoặc "việc làm"
                job_links = soup.find_all('a', href=lambda href: href and ('job' in href.lower() or 'viec-lam' in href.lower()))
                for link in job_links:
                    url = link.get('href')
                    if not url.startswith('http'):
                        url = site['url'] + url
                    
                    links.append({
                        'url': url,
                        'title': clean_text(link.text),
                        'company': '',  # Không có thông tin công ty
                        'site': site['name'],
                    })
        
        except Exception as e:
            logger.error(f"Lỗi khi parse HTML từ trang {site['name']}: {e}")
        
        return links
    
    def crawl_job_details(self, job_links=None):
        """
        Crawl chi tiết công việc từ danh sách link
        
        Args:
            job_links (list): Danh sách link tuyển dụng
        
        Returns:
            list: Danh sách chi tiết công việc
        """
        job_details = []
        
        # Nếu không có danh sách link, đọc từ file
        if not job_links:
            job_links = load_from_csv(JOB_LINK_FILE)
        
        # Crawl từng link
        for job in job_links:
            try:
                logger.info(f"Đang crawl chi tiết công việc: {job['title']}")
                
                # Crawl chi tiết
                if self.use_selenium:
                    detail = self._crawl_detail_selenium(job['url'], job['site'])
                else:
                    detail = self._crawl_detail_requests(job['url'], job['site'])
                
                # Thêm thông tin cơ bản
                if detail:
                    detail.update({
                        'url': job['url'],
                        'title': job['title'],
                        'company': job['company'],
                        'site': job['site'],
                    })
                    
                    job_details.append(detail)
                    logger.info(f"Đã crawl chi tiết công việc: {job['title']}")
                else:
                    logger.warning(f"Không thể crawl chi tiết công việc: {job['title']}")
                
                # Delay để tránh bị chặn
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.error(f"Lỗi khi crawl chi tiết công việc {job['title']}: {e}")
                continue
        
        # Lưu danh sách chi tiết vào file
        if job_details:
            save_to_csv(job_details, JOB_DATA_FILE)
            logger.info(f"Đã lưu {len(job_details)} chi tiết công việc vào file {JOB_DATA_FILE}")
        
        return job_details
    
    def _crawl_detail_selenium(self, url, site_name):
        """
        Crawl chi tiết công việc bằng Selenium
        
        Args:
            url (str): URL cần crawl
            site_name (str): Tên trang
        
        Returns:
            dict: Chi tiết công việc
        """
        if not self.driver:
            logger.error("Selenium WebDriver chưa được khởi tạo")
            return {}
        
        try:
            # Truy cập URL
            self.driver.get(url)
            
            # Đợi trang load xong
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Lấy HTML
            html = self.driver.page_source
            
            # Parse HTML
            return self._parse_job_detail(html, site_name)
        except Exception as e:
            logger.error(f"Lỗi khi crawl chi tiết công việc {url} bằng Selenium: {e}")
            return {}
    
    def _crawl_detail_requests(self, url, site_name):
        """
        Crawl chi tiết công việc bằng Requests
        
        Args:
            url (str): URL cần crawl
            site_name (str): Tên trang
        
        Returns:
            dict: Chi tiết công việc
        """
        try:
            # Gửi request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            return self._parse_job_detail(response.text, site_name)
        except Exception as e:
            logger.error(f"Lỗi khi crawl chi tiết công việc {url} bằng Requests: {e}")
            return {}
    
    def _parse_job_detail(self, html, site_name):
        """
        Parse HTML để lấy chi tiết công việc
        
        Args:
            html (str): HTML cần parse
            site_name (str): Tên trang
        
        Returns:
            dict: Chi tiết công việc
        """
        detail = {}
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'lxml')
            
            # Tùy theo từng trang mà có cách parse khác nhau
            if site_name == "VietnamWorks":
                # Địa điểm
                location_elem = soup.select_one('.location-name')
                if location_elem:
                    detail['location'] = clean_text(location_elem.text)
                
                # Mức lương
                salary_elem = soup.select_one('.salary-text')
                if salary_elem:
                    detail['salary'] = clean_text(salary_elem.text)
                
                # Mô tả công việc
                description_elem = soup.select_one('.job-description')
                if description_elem:
                    detail['description'] = clean_text(description_elem.text)
                
                # Yêu cầu
                requirement_elem = soup.select_one('.job-requirement')
                if requirement_elem:
                    detail['requirement'] = clean_text(requirement_elem.text)
                
                # Lợi ích
                benefit_elem = soup.select_one('.job-benefit')
                if benefit_elem:
                    detail['benefit'] = clean_text(benefit_elem.text)
            
            elif site_name == "TopCV":
                # Địa điểm
                location_elem = soup.select_one('.job-location')
                if location_elem:
                    detail['location'] = clean_text(location_elem.text)
                
                # Mức lương
                salary_elem = soup.select_one('.job-salary')
                if salary_elem:
                    detail['salary'] = clean_text(salary_elem.text)
                
                # Mô tả công việc
                description_elem = soup.select_one('.job-description')
                if description_elem:
                    detail['description'] = clean_text(description_elem.text)
                
                # Yêu cầu
                requirement_elem = soup.select_one('.job-requirement')
                if requirement_elem:
                    detail['requirement'] = clean_text(requirement_elem.text)
                
                # Lợi ích
                benefit_elem = soup.select_one('.job-benefit')
                if benefit_elem:
                    detail['benefit'] = clean_text(benefit_elem.text)
            
            # Thêm các trang khác tương tự...
            # Đây chỉ là ví dụ, cần cập nhật cho từng trang cụ thể
            
            else:
                # Mặc định tìm các thông tin cơ bản
                # Địa điểm
                location_elems = soup.find_all(['span', 'div', 'p'], text=lambda t: t and ('location' in t.lower() or 'địa điểm' in t.lower() or 'địa chỉ' in t.lower()))
                for elem in location_elems:
                    if elem.parent:
                        detail['location'] = clean_text(elem.parent.text)
                        break
                
                # Mức lương
                salary_elems = soup.find_all(['span', 'div', 'p'], text=lambda t: t and ('salary' in t.lower() or 'lương' in t.lower()))
                for elem in salary_elems:
                    if elem.parent:
                        detail['salary'] = clean_text(elem.parent.text)
                        break
                
                # Mô tả công việc
                description_elems = soup.find_all(['h2', 'h3', 'h4'], text=lambda t: t and ('job description' in t.lower() or 'mô tả công việc' in t.lower()))
                for elem in description_elems:
                    if elem.find_next():
                        detail['description'] = clean_text(elem.find_next().text)
                        break
                
                # Yêu cầu
                requirement_elems = soup.find_all(['h2', 'h3', 'h4'], text=lambda t: t and ('requirement' in t.lower() or 'yêu cầu' in t.lower()))
                for elem in requirement_elems:
                    if elem.find_next():
                        detail['requirement'] = clean_text(elem.find_next().text)
                        break
                
                # Lợi ích
                benefit_elems = soup.find_all(['h2', 'h3', 'h4'], text=lambda t: t and ('benefit' in t.lower() or 'lợi ích' in t.lower() or 'phúc lợi' in t.lower()))
                for elem in benefit_elems:
                    if elem.find_next():
                        detail['benefit'] = clean_text(elem.find_next().text)
                        break
        
        except Exception as e:
            logger.error(f"Lỗi khi parse HTML chi tiết công việc từ trang {site_name}: {e}")
        
        return detail 