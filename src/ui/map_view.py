#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module xử lý chức năng bản đồ
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView

from src.utils.config import GOOGLE_MAPS_API_KEY
from src.utils.logger import get_logger
from src.utils.helper import geocode_address

# Khởi tạo logger
logger = get_logger()

class MapDialog(QDialog):
    """
    Dialog hiển thị bản đồ
    """
    
    # Định nghĩa signal
    location_selected = pyqtSignal(str, float, float)
    
    def __init__(self, parent=None):
        """
        Khởi tạo dialog
        
        Args:
            parent (QWidget): Widget cha
        """
        super().__init__(parent)
        
        # Thiết lập dialog
        self.setWindowTitle("Chọn vị trí")
        self.setMinimumSize(800, 600)
        
        # Thiết lập giao diện
        self._setup_ui()
        
        # Kết nối các signal
        self._connect_signals()
        
        # Khởi tạo bản đồ
        self._init_map()
        
        logger.info("Đã khởi tạo dialog bản đồ")
    
    def _setup_ui(self):
        """
        Thiết lập giao diện
        """
        # Tạo layout chính
        main_layout = QVBoxLayout(self)
        
        # Tạo thanh tìm kiếm
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập địa chỉ cần tìm...")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Tìm kiếm")
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout)
        
        # Tạo widget bản đồ
        self.map_widget = QWebEngineView()
        main_layout.addWidget(self.map_widget)
        
        # Tạo thanh thông tin
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel()
        info_layout.addWidget(self.info_label)
        
        self.select_button = QPushButton("Chọn vị trí này")
        self.select_button.setEnabled(False)
        info_layout.addWidget(self.select_button)
        
        main_layout.addLayout(info_layout)
    
    def _connect_signals(self):
        """
        Kết nối các signal
        """
        # Kết nối nút tìm kiếm
        self.search_button.clicked.connect(self._search_location)
        
        # Kết nối nút chọn vị trí
        self.select_button.clicked.connect(self._select_location)
        
        # Kết nối sự kiện nhấn Enter trong ô tìm kiếm
        self.search_input.returnPressed.connect(self._search_location)
    
    def _init_map(self):
        """
        Khởi tạo bản đồ
        """
        if not GOOGLE_MAPS_API_KEY:
            logger.error("Chưa cấu hình Google Maps API key")
            return
        
        # Tạo HTML cho bản đồ
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Maps</title>
            <style>
                #map {{
                    height: 100%;
                    width: 100%;
                }}
                html, body {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
            </style>
            <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}"></script>
            <script>
                var map;
                var marker;
                
                function initMap() {{
                    // Vị trí mặc định (Hà Nội)
                    var defaultLocation = {{lat: 21.0285, lng: 105.8542}};
                    
                    // Tạo bản đồ
                    map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 12,
                        center: defaultLocation
                    }});
                    
                    // Tạo marker
                    marker = new google.maps.Marker({{
                        position: defaultLocation,
                        map: map,
                        draggable: true
                    }});
                    
                    // Xử lý sự kiện kéo marker
                    marker.addListener('dragend', function() {{
                        var position = marker.getPosition();
                        updateLocation(position.lat(), position.lng());
                    }});
                    
                    // Xử lý sự kiện click trên bản đồ
                    map.addListener('click', function(event) {{
                        marker.setPosition(event.latLng);
                        updateLocation(event.latLng.lat(), event.latLng.lng());
                    }});
                }}
                
                function updateLocation(lat, lng) {{
                    // Gửi tọa độ về Python
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        channel.objects.handler.handleLocationUpdate(lat, lng);
                    }});
                }}
                
                function setLocation(lat, lng) {{
                    // Di chuyển bản đồ và marker đến vị trí mới
                    var position = new google.maps.LatLng(lat, lng);
                    map.setCenter(position);
                    marker.setPosition(position);
                }}
            </script>
        </head>
        <body onload="initMap()">
            <div id="map"></div>
        </body>
        </html>
        """
        
        # Load HTML vào widget
        self.map_widget.setHtml(html)
    
    def _search_location(self):
        """
        Tìm kiếm địa điểm
        """
        # Lấy địa chỉ cần tìm
        address = self.search_input.text().strip()
        if not address:
            return
        
        try:
            # Chuyển đổi địa chỉ thành tọa độ
            location = geocode_address(address)
            if location:
                # Cập nhật vị trí trên bản đồ
                self.map_widget.page().runJavaScript(
                    f"setLocation({location['lat']}, {location['lng']})"
                )
                
                # Cập nhật thông tin
                self.info_label.setText(location['formatted_address'])
                self.select_button.setEnabled(True)
                
                # Lưu thông tin vị trí
                self.current_location = location
            else:
                self.info_label.setText("Không tìm thấy địa điểm")
                self.select_button.setEnabled(False)
                self.current_location = None
        
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm địa điểm: {e}")
            self.info_label.setText("Lỗi khi tìm kiếm địa điểm")
            self.select_button.setEnabled(False)
            self.current_location = None
    
    def _select_location(self):
        """
        Chọn vị trí hiện tại
        """
        if self.current_location:
            # Phát signal với thông tin vị trí
            self.location_selected.emit(
                self.current_location['formatted_address'],
                self.current_location['lat'],
                self.current_location['lng']
            )
            
            # Đóng dialog
            self.accept()
    
    def handle_location_update(self, lat, lng):
        """
        Xử lý sự kiện cập nhật vị trí từ JavaScript
        
        Args:
            lat (float): Vĩ độ
            lng (float): Kinh độ
        """
        try:
            # Chuyển đổi tọa độ thành địa chỉ
            location = geocode_address(f"{lat},{lng}")
            if location:
                # Cập nhật thông tin
                self.info_label.setText(location['formatted_address'])
                self.select_button.setEnabled(True)
                
                # Lưu thông tin vị trí
                self.current_location = location
            else:
                self.info_label.setText("Không thể xác định địa chỉ")
                self.select_button.setEnabled(False)
                self.current_location = None
        
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật vị trí: {e}")
            self.info_label.setText("Lỗi khi cập nhật vị trí")
            self.select_button.setEnabled(False)
            self.current_location = None 