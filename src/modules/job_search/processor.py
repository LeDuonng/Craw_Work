#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module xử lý dữ liệu tuyển dụng
"""

import os
import re
import pandas as pd
from datetime import datetime

from src.utils.config import JOB_DATA_FILE, EXPERIENCE_LEVELS, JOB_TYPES, WORK_MODES
from src.utils.logger import get_logger
from src.utils.helper import clean_text, extract_salary, calculate_distance, geocode_address, load_from_csv, save_to_csv

# Khởi tạo logger
logger = get_logger()

class JobProcessor:
    """
    Class xử lý dữ liệu tuyển dụng
    """
    
    def __init__(self, user_location=None):
        """
        Khởi tạo processor
        
        Args:
            user_location (str): Vị trí của người dùng
        """
        self.user_location = user_location
        self.user_coordinates = None
        
        # Chuyển đổi địa chỉ người dùng thành tọa độ
        if self.user_location:
            location_data = geocode_address(self.user_location)
            if location_data:
                self.user_coordinates = (location_data['lat'], location_data['lng'])
                self.user_location = location_data['formatted_address']
                logger.info(f"Đã chuyển đổi địa chỉ người dùng thành tọa độ: {self.user_coordinates}")
            else:
                logger.warning(f"Không thể chuyển đổi địa chỉ người dùng: {self.user_location}")
    
    def process_jobs(self, jobs=None, filters=None):
        """
        Xử lý danh sách công việc
        
        Args:
            jobs (list): Danh sách công việc
            filters (dict): Bộ lọc
        
        Returns:
            list: Danh sách công việc đã xử lý
        """
        # Nếu không có danh sách công việc, đọc từ file
        if not jobs:
            jobs = load_from_csv(JOB_DATA_FILE)
        
        if not jobs:
            logger.warning("Không có dữ liệu công việc để xử lý")
            return []
        
        # Xử lý từng công việc
        processed_jobs = []
        for job in jobs:
            try:
                # Làm sạch dữ liệu
                processed_job = self._clean_job_data(job)
                
                # Tính khoảng cách
                if self.user_coordinates and 'location' in processed_job:
                    distance = calculate_distance(self.user_location, processed_job['location'])
                    processed_job['distance'] = distance
                
                # Thêm vào danh sách
                processed_jobs.append(processed_job)
            except Exception as e:
                logger.error(f"Lỗi khi xử lý công việc {job.get('title', '')}: {e}")
                continue
        
        # Lọc dữ liệu
        if filters:
            processed_jobs = self._filter_jobs(processed_jobs, filters)
        
        # Sắp xếp dữ liệu
        processed_jobs = self._sort_jobs(processed_jobs)
        
        return processed_jobs
    
    def _clean_job_data(self, job):
        """
        Làm sạch dữ liệu công việc
        
        Args:
            job (dict): Dữ liệu công việc
        
        Returns:
            dict: Dữ liệu công việc đã làm sạch
        """
        cleaned_job = job.copy()
        
        # Làm sạch tiêu đề
        if 'title' in cleaned_job:
            cleaned_job['title'] = clean_text(cleaned_job['title'])
        
        # Làm sạch công ty
        if 'company' in cleaned_job:
            cleaned_job['company'] = clean_text(cleaned_job['company'])
        
        # Làm sạch địa điểm
        if 'location' in cleaned_job:
            cleaned_job['location'] = clean_text(cleaned_job['location'])
        
        # Làm sạch mức lương
        if 'salary' in cleaned_job:
            cleaned_job['salary'] = clean_text(cleaned_job['salary'])
            # Trích xuất mức lương
            salary_range = extract_salary(cleaned_job['salary'])
            if salary_range:
                cleaned_job['salary_range'] = salary_range
        
        # Làm sạch mô tả
        if 'description' in cleaned_job:
            cleaned_job['description'] = clean_text(cleaned_job['description'])
        
        # Làm sạch yêu cầu
        if 'requirement' in cleaned_job:
            cleaned_job['requirement'] = clean_text(cleaned_job['requirement'])
        
        # Làm sạch lợi ích
        if 'benefit' in cleaned_job:
            cleaned_job['benefit'] = clean_text(cleaned_job['benefit'])
        
        # Xác định kinh nghiệm
        if 'requirement' in cleaned_job:
            experience = self._extract_experience(cleaned_job['requirement'])
            if experience:
                cleaned_job['experience'] = experience
        
        # Xác định loại công việc
        if 'description' in cleaned_job:
            job_type = self._extract_job_type(cleaned_job['description'])
            if job_type:
                cleaned_job['job_type'] = job_type
        
        # Xác định chế độ làm việc
        if 'description' in cleaned_job:
            work_mode = self._extract_work_mode(cleaned_job['description'])
            if work_mode:
                cleaned_job['work_mode'] = work_mode
        
        return cleaned_job
    
    def _extract_experience(self, text):
        """
        Trích xuất kinh nghiệm từ văn bản
        
        Args:
            text (str): Văn bản
        
        Returns:
            str: Kinh nghiệm
        """
        if not text:
            return None
        
        text = text.lower()
        
        # Tìm kiếm các mẫu kinh nghiệm
        for exp in EXPERIENCE_LEVELS:
            if exp.lower() in text:
                return exp
        
        # Tìm kiếm các mẫu số năm kinh nghiệm
        patterns = [
            r'(\d+)\s*năm\s*kinh\s*nghiệm',
            r'(\d+)\s*years?\s*experience',
            r'(\d+)\s*years?\s*of\s*experience',
            r'experience\s*:\s*(\d+)\s*years?',
            r'kinh\s*nghiệm\s*:\s*(\d+)\s*năm',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                if years == 0:
                    return "No experience"
                elif years < 1:
                    return "Intern"
                elif years < 2:
                    return "Fresher"
                elif years < 3:
                    return "Junior"
                elif years < 5:
                    return "Mid"
                else:
                    return "Senior"
        
        return None
    
    def _extract_job_type(self, text):
        """
        Trích xuất loại công việc từ văn bản
        
        Args:
            text (str): Văn bản
        
        Returns:
            str: Loại công việc
        """
        if not text:
            return None
        
        text = text.lower()
        
        # Tìm kiếm các mẫu loại công việc
        for job_type in JOB_TYPES:
            if job_type.lower() in text:
                return job_type
        
        return None
    
    def _extract_work_mode(self, text):
        """
        Trích xuất chế độ làm việc từ văn bản
        
        Args:
            text (str): Văn bản
        
        Returns:
            str: Chế độ làm việc
        """
        if not text:
            return None
        
        text = text.lower()
        
        # Tìm kiếm các mẫu chế độ làm việc
        for work_mode in WORK_MODES:
            if work_mode.lower() in text:
                return work_mode
        
        # Tìm kiếm các mẫu từ khóa
        if 'remote' in text or 'từ xa' in text or 'tại nhà' in text:
            return "Remote"
        elif 'hybrid' in text or 'kết hợp' in text:
            return "Hybrid"
        elif 'on-site' in text or 'tại văn phòng' in text or 'tại công ty' in text:
            return "On-site"
        
        return "Not specified"
    
    def _filter_jobs(self, jobs, filters):
        """
        Lọc danh sách công việc
        
        Args:
            jobs (list): Danh sách công việc
            filters (dict): Bộ lọc
        
        Returns:
            list: Danh sách công việc đã lọc
        """
        filtered_jobs = jobs.copy()
        
        # Lọc theo địa điểm
        if 'locations' in filters and filters['locations']:
            filtered_jobs = [job for job in filtered_jobs if 'location' in job and any(location.lower() in job['location'].lower() for location in filters['locations'])]
        
        # Lọc theo kinh nghiệm
        if 'experience' in filters and filters['experience']:
            filtered_jobs = [job for job in filtered_jobs if 'experience' in job and job['experience'] == filters['experience']]
        
        # Lọc theo mức lương
        if 'salary_min' in filters and filters['salary_min']:
            # Cần xử lý phức tạp hơn để so sánh mức lương
            pass
        
        if 'salary_max' in filters and filters['salary_max']:
            # Cần xử lý phức tạp hơn để so sánh mức lương
            pass
        
        # Lọc theo loại công việc
        if 'job_type' in filters and filters['job_type']:
            filtered_jobs = [job for job in filtered_jobs if 'job_type' in job and job['job_type'] == filters['job_type']]
        
        # Lọc theo chế độ làm việc
        if 'work_mode' in filters and filters['work_mode']:
            filtered_jobs = [job for job in filtered_jobs if 'work_mode' in job and job['work_mode'] == filters['work_mode']]
        
        # Lọc theo kỹ năng
        if 'skills' in filters and filters['skills']:
            filtered_jobs = [job for job in filtered_jobs if 'requirement' in job and any(skill.lower() in job['requirement'].lower() for skill in filters['skills'])]
        
        # Lọc theo khoảng cách
        if 'distance_max' in filters and filters['distance_max'] and self.user_coordinates:
            filtered_jobs = [job for job in filtered_jobs if 'distance' in job and job['distance'] and job['distance'] <= filters['distance_max']]
        
        return filtered_jobs
    
    def _sort_jobs(self, jobs, sort_by='distance'):
        """
        Sắp xếp danh sách công việc
        
        Args:
            jobs (list): Danh sách công việc
            sort_by (str): Tiêu chí sắp xếp
        
        Returns:
            list: Danh sách công việc đã sắp xếp
        """
        if not jobs:
            return []
        
        # Chuyển đổi sang DataFrame để dễ sắp xếp
        df = pd.DataFrame(jobs)
        
        # Sắp xếp theo tiêu chí
        if sort_by == 'distance' and 'distance' in df.columns:
            # Sắp xếp theo khoảng cách (tăng dần)
            df = df.sort_values(by='distance', ascending=True, na_position='last')
        elif sort_by == 'salary' and 'salary_range' in df.columns:
            # Sắp xếp theo mức lương (giảm dần)
            df = df.sort_values(by='salary_range', ascending=False, na_position='last')
        elif sort_by == 'date' and 'date' in df.columns:
            # Sắp xếp theo ngày đăng (giảm dần)
            df = df.sort_values(by='date', ascending=False, na_position='last')
        
        # Chuyển đổi lại thành list
        return df.to_dict('records')
    
    def export_to_csv(self, jobs, filename=None):
        """
        Xuất danh sách công việc ra file CSV
        
        Args:
            jobs (list): Danh sách công việc
            filename (str): Tên file
        
        Returns:
            bool: Kết quả xuất file
        """
        if not filename:
            # Tạo tên file mặc định
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"job_opportunities_{timestamp}.csv"
        
        # Xuất ra file
        return save_to_csv(jobs, filename) 