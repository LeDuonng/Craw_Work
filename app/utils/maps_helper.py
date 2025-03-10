"""
Google Maps API helper functions
"""
import googlemaps
from app.utils.config import GOOGLE_MAPS_API_KEY

# Khởi tạo client Google Maps
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def geocode_address(address):
    """
    Chuyển đổi địa chỉ thành tọa độ (lat, lng)
    
    Args:
        address (str): Địa chỉ cần chuyển đổi
        
    Returns:
        tuple: (latitude, longitude) hoặc None nếu không tìm thấy
    """
    try:
        if not address:
            return None
        
        # Geocode địa chỉ
        geocode_result = gmaps.geocode(address)
        
        if geocode_result and len(geocode_result) > 0:
            location = geocode_result[0]['geometry']['location']
            return (location['lat'], location['lng'])
        
        return None
    except Exception as e:
        print(f"Lỗi khi geocode địa chỉ: {e}")
        return None

def calculate_distance(origin, destination):
    """
    Tính khoảng cách giữa hai địa điểm
    
    Args:
        origin (tuple): Tọa độ điểm xuất phát (lat, lng)
        destination (tuple): Tọa độ điểm đến (lat, lng)
        
    Returns:
        float: Khoảng cách (km) hoặc None nếu có lỗi
    """
    try:
        if not origin or not destination:
            return None
        
        # Tính khoảng cách
        distance_result = gmaps.distance_matrix(
            origins=[origin],
            destinations=[destination],
            mode="driving",
            units="metric"
        )
        
        if distance_result['status'] == 'OK':
            # Lấy khoảng cách
            distance = distance_result['rows'][0]['elements'][0]['distance']['value']
            # Chuyển đổi từ mét sang km
            return distance / 1000
        
        return None
    except Exception as e:
        print(f"Lỗi khi tính khoảng cách: {e}")
        return None

def get_districts_in_province(province):
    """
    Lấy danh sách quận/huyện trong một tỉnh/thành phố
    
    Args:
        province (str): Tên tỉnh/thành phố
        
    Returns:
        list: Danh sách quận/huyện hoặc None nếu có lỗi
    """
    try:
        # Geocode tỉnh/thành phố
        geocode_result = gmaps.geocode(
            province + ", Vietnam",
            region="vn"
        )
        
        if not geocode_result:
            return None
        
        # Lấy tọa độ của tỉnh/thành phố
        location = geocode_result[0]['geometry']['location']
        
        # Tìm kiếm các quận/huyện gần đó
        places_result = gmaps.places_nearby(
            location=(location['lat'], location['lng']),
            radius=50000,  # 50km
            type='administrative_area_level_2'
        )
        
        districts = []
        if 'results' in places_result:
            for place in places_result['results']:
                districts.append(place['name'])
        
        return districts
    except Exception as e:
        print(f"Lỗi khi lấy danh sách quận/huyện: {e}")
        return None

def get_place_details(place_id):
    """
    Lấy thông tin chi tiết về một địa điểm
    
    Args:
        place_id (str): ID của địa điểm
        
    Returns:
        dict: Thông tin chi tiết về địa điểm hoặc None nếu có lỗi
    """
    try:
        place_details = gmaps.place(place_id)
        return place_details
    except Exception as e:
        print(f"Lỗi khi lấy thông tin chi tiết địa điểm: {e}")
        return None 