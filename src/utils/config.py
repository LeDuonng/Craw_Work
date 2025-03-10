#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module quản lý cấu hình ứng dụng
"""

import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Cấu hình ứng dụng
APP_NAME = os.getenv("APP_NAME", "CrawWork")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Cấu hình đường dẫn
DATA_DIR = os.getenv("DATA_DIR", "src/data")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

# Cấu hình API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Cấu hình crawl
JOB_LINK_FILE = os.path.join(OUTPUT_DIR, "job_link_list.csv")
JOB_DATA_FILE = os.path.join(OUTPUT_DIR, "job_opportunities.csv")

# Danh sách các trang tuyển dụng hỗ trợ
JOB_SITES = {
    "vietnamworks": {
        "name": "VietnamWorks",
        "url": "https://www.vietnamworks.com",
        "search_url": "https://www.vietnamworks.com/tim-viec-lam/{}?page={}",
    },
    "topcv": {
        "name": "TopCV",
        "url": "https://www.topcv.vn",
        "search_url": "https://www.topcv.vn/tim-viec-lam-{}?page={}",
    },
    "careerviet": {
        "name": "CareerViet",
        "url": "https://careerviet.vn",
        "search_url": "https://careerviet.vn/viec-lam/{}?page={}",
    },
    "jobsgo": {
        "name": "JobsGO",
        "url": "https://jobsgo.vn",
        "search_url": "https://jobsgo.vn/viec-lam-{}?page={}",
    },
    "careerlink": {
        "name": "CareerLink",
        "url": "https://www.careerlink.vn",
        "search_url": "https://www.careerlink.vn/tim-viec-lam/{}?page={}",
    },
    "timviecnhanh": {
        "name": "Timviecnhanh",
        "url": "https://timviecnhanh.com",
        "search_url": "https://timviecnhanh.com/tim-viec-lam-{}?page={}",
    },
    "jobstreet": {
        "name": "JobStreet",
        "url": "https://www.jobstreet.vn",
        "search_url": "https://www.jobstreet.vn/j?q={}&page={}",
    },
    "glints": {
        "name": "Glints",
        "url": "https://glints.com/vn",
        "search_url": "https://glints.com/vn/opportunities/jobs/explore?keyword={}&page={}",
    },
    "itviec": {
        "name": "ITviec",
        "url": "https://itviec.com",
        "search_url": "https://itviec.com/tim-viec-{}?page={}",
    },
    "123job": {
        "name": "123Job",
        "url": "https://123job.vn",
        "search_url": "https://123job.vn/tuyen-dung?q={}&page={}",
    },
}

# Cấu hình kinh nghiệm
EXPERIENCE_LEVELS = [
    "No experience",
    "Intern",
    "Fresher",
    "Junior",
    "Entry",
    "Mid",
    "Senior",
]

# Cấu hình loại công việc
JOB_TYPES = [
    "Full-time",
    "Part-time",
    "Contract",
    "Temporary",
    "Internship",
    "Freelance",
]

# Cấu hình chế độ làm việc
WORK_MODES = [
    "Remote",
    "Hybrid",
    "On-site",
    "Not specified",
]

# Cấu hình yêu cầu ngôn ngữ
LANGUAGE_REQUIREMENTS = [
    "Vietnamese",
    "English",
    "Both",
    "Other",
]