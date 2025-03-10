#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module chứa các hàm tiện ích
"""

import os
import re
import json
import pandas as pd
import googlemaps
from datetime import datetime
from .config import GOOGLE_MAPS_API_KEY
from .logger import get_logger

# Khởi tạo logger
logger = get_logger()

# Khởi tạo Google Maps client
gmaps = None
if GOOGLE_MAPS_API_KEY:
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    except Exception as e:
        logger.error(f"Không thể khởi tạo Google Maps client: {e}")

def clean_text(text):
    """
    Làm sạch văn bản
    """
    if not text:
        return ""
    
    # Loại bỏ HTML tags
    text = re.sub(r'<.*?>', ' ', text)
    
    # Loại bỏ ký tự đặc biệt và khoảng trắng thừa
    text = re.sub(r'[^\w\s\.,;:!?]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_salary(text):
    """
    Trích xuất thông tin lương từ văn bản
    """
    if not text:
        return None
    
    # Tìm kiếm các mẫu lương phổ biến
    patterns = [
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(triệu|tr|million|M)',
        r'(\d+(?:\.\d+)?)\s*(triệu|tr|million|M)',
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(USD|$)',
        r'(\d+(?:\.\d+)?)\s*(USD|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def calculate_distance(origin, destination):
    """
    Tính khoảng cách giữa hai địa điểm
    """
    if not gmaps or not origin or not destination:
        return None
    
    try:
        # Gọi API để tính khoảng cách
        result = gmaps.distance_matrix(origin, destination, mode="driving")
        
        # Kiểm tra kết quả
        if result['status'] == 'OK':
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                # Trả về khoảng cách tính bằng km
                distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000
                return round(distance, 2)
    except Exception as e:
        logger.error(f"Lỗi khi tính khoảng cách: {e}")
    
    return None

def geocode_address(address):
    """
    Chuyển đổi địa chỉ thành tọa độ
    """
    if not gmaps or not address:
        return None
    
    try:
        # Gọi API để lấy tọa độ
        result = gmaps.geocode(address)
        
        # Kiểm tra kết quả
        if result and len(result) > 0:
            location = result[0]['geometry']['location']
            return {
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': result[0]['formatted_address']
            }
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi địa chỉ: {e}")
    
    return None

def save_to_csv(data, filename, mode='w'):
    """
    Lưu dữ liệu vào file CSV
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, mode=mode, encoding='utf-8-sig')
        logger.info(f"Đã lưu dữ liệu vào file {filename}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu dữ liệu vào file {filename}: {e}")
        return False

def load_from_csv(filename):
    """
    Đọc dữ liệu từ file CSV
    """
    try:
        if os.path.exists(filename):
            df = pd.read_csv(filename, encoding='utf-8-sig')
            logger.info(f"Đã đọc dữ liệu từ file {filename}")
            return df.to_dict('records')
        else:
            logger.warning(f"File {filename} không tồn tại")
            return []
    except Exception as e:
        logger.error(f"Lỗi khi đọc dữ liệu từ file {filename}: {e}")
        return []

def format_date(date_str, input_format='%Y-%m-%d', output_format='%d/%m/%Y'):
    """
    Định dạng lại ngày tháng
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except Exception:
        return date_str 