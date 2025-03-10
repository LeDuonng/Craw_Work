"""
OpenAI API helper functions
"""
import openai
import json
import logging
from app.utils.config import OPENAI_API_KEY

# Cấu hình OpenAI API
openai.api_key = OPENAI_API_KEY

# Thiết lập logger
logger = logging.getLogger(__name__)

def extract_job_info_with_openai(html_content, url):
    """
    Sử dụng OpenAI để trích xuất thông tin việc làm từ HTML
    
    Args:
        html_content (str): Nội dung HTML của trang việc làm
        url (str): URL của trang việc làm
        
    Returns:
        dict: Thông tin chi tiết về việc làm
    """
    try:
        # Cắt bớt HTML nếu quá dài để tránh vượt quá giới hạn token
        if len(html_content) > 100000:
            html_content = html_content[:100000]
        
        # Tạo prompt cho OpenAI
        prompt = f"""
        Phân tích nội dung HTML sau đây từ trang tuyển dụng việc làm và trích xuất các thông tin sau:
        1. Tiêu đề công việc
        2. Tên công ty
        3. Địa chỉ công ty
        4. Địa điểm làm việc
        5. Mức lương (nếu có)
        6. Loại công việc (toàn thời gian, bán thời gian, v.v.)
        7. Hình thức làm việc (tại văn phòng, từ xa, hybrid)
        8. Kỹ năng yêu cầu (liệt kê)
        9. Mức kinh nghiệm
        10. Yêu cầu học vấn
        11. Mô tả công việc ngắn gọn
        12. Lợi ích công việc
        13. Hạn nộp hồ sơ
        14. Yêu cầu ngôn ngữ
        15. Email liên hệ (nếu có)
        16. Người liên hệ (nếu có)
        
        URL: {url}
        
        HTML:
        {html_content}
        
        Trả về kết quả dưới dạng JSON với các trường tương ứng. Nếu không tìm thấy thông tin, hãy để trống hoặc ghi "Không có thông tin".
        """
        
        try:
            # Thử sử dụng GPT-3.5-turbo với response_format
            logger.info(f"Gọi OpenAI API để trích xuất thông tin từ {url}")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý AI chuyên phân tích nội dung trang web tuyển dụng việc làm. Nhiệm vụ của bạn là trích xuất thông tin chi tiết từ HTML của trang tuyển dụng."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            # Phân tích kết quả JSON
            result = response.choices[0].message.content
            job_info = json.loads(result)
            
        except Exception as api_error:
            # Nếu có lỗi với response_format, thử lại không có tham số đó
            logger.warning(f"Lỗi khi sử dụng response_format, thử lại không có tham số này: {api_error}")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý AI chuyên phân tích nội dung trang web tuyển dụng việc làm. Nhiệm vụ của bạn là trích xuất thông tin chi tiết từ HTML của trang tuyển dụng và trả về kết quả dưới dạng JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Phân tích kết quả JSON từ văn bản
            result = response.choices[0].message.content
            
            # Trích xuất phần JSON từ văn bản (có thể có văn bản khác xung quanh)
            try:
                # Tìm dấu { đầu tiên và } cuối cùng
                start_idx = result.find('{')
                end_idx = result.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx]
                    job_info = json.loads(json_str)
                else:
                    # Nếu không tìm thấy định dạng JSON, tạo một cấu trúc mặc định
                    job_info = {"job_title": "Không thể trích xuất", "error": "Không tìm thấy dữ liệu JSON"}
            except json.JSONDecodeError:
                job_info = {"job_title": "Không thể trích xuất", "error": "Không thể phân tích JSON"}
        
        logger.info(f"Đã trích xuất thông tin từ {url} thành công")
        return job_info
    except Exception as e:
        logger.error(f"Lỗi khi sử dụng OpenAI API: {e}")
        # Trả về thông tin mặc định nếu có lỗi
        return {
            "job_title": "Không thể trích xuất",
            "company_name": "Không thể trích xuất",
            "company_address": "",
            "job_location": "",
            "salary_range": "",
            "job_type": "",
            "work_mode": "",
            "required_skills": "",
            "experience_level": "",
            "education_requirements": "",
            "brief_job_description": "",
            "job_benefits": "",
            "application_deadline": "",
            "language_requirement": "",
            "contact_email": "",
            "contact_person": "",
            "error": str(e)
        }

def search_jobs_with_openai(keywords, base_url, location=None, filters=None):
    """
    Sử dụng OpenAI để tìm kiếm việc làm phù hợp dựa trên từ khóa và các bộ lọc
    
    Args:
        keywords (list): Danh sách từ khóa tìm kiếm
        base_url (str): URL cơ sở của trang web việc làm
        location (dict, optional): Thông tin vị trí địa lý
        filters (dict, optional): Các bộ lọc bổ sung
        
    Returns:
        list: Danh sách các URL việc làm được đề xuất
    """
    try:
        # Xây dựng mô tả yêu cầu tìm kiếm
        keywords_str = ", ".join(keywords)
        location_str = ""
        if location:
            if 'user_province' in location:
                location_str += f"Tỉnh/thành phố: {location['user_province']} "
            if 'user_district' in location:
                location_str += f"Quận/huyện: {location['user_district']} "
            if 'company_province' in location:
                location_str += f"Tại địa điểm công ty: {location['company_province']} "
        
        filters_str = ""
        if filters:
            for key, value in filters.items():
                filters_str += f"{key}: {value}, "
        
        prompt = f"""
        Bạn là trợ lý AI chuyên tìm kiếm việc làm. Hãy tìm kiếm việc làm dựa trên các thông tin sau:
        
        Từ khóa tìm kiếm: {keywords_str}
        Địa điểm: {location_str}
        Bộ lọc bổ sung: {filters_str}
        
        Trang web cần tìm: {base_url}
        
        Hãy thực hiện nghiên cứu sâu (deep research) và phân tích ngữ nghĩa để tìm các việc làm phù hợp nhất.
        KHÔNG chỉ tìm kiếm theo cách ghép từ khóa vào URL.
        Phân tích ý nghĩa của từ khóa và tìm các công việc liên quan, thậm chí nếu không chứa chính xác từ khóa.
        
        Trả về danh sách các URL công việc phù hợp nhất dưới dạng mảng JSON. Mỗi URL phải bắt đầu bằng {base_url}.
        """
        
        logger.info(f"Gọi OpenAI API để tìm kiếm việc làm với từ khóa: {keywords_str}")
        
        try:
            # Thử sử dụng GPT-4 với response_format
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý AI chuyên tìm kiếm việc làm. Bạn có khả năng thực hiện tìm kiếm thông minh, phân tích ngữ nghĩa, và hiểu nhu cầu người dùng."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Phân tích kết quả JSON
            result = response.choices[0].message.content
            data = json.loads(result)
            job_urls = data.get("urls", [])
            
        except Exception as api_error:
            # Nếu có lỗi với response_format, thử lại với GPT-3.5 không có tham số đó
            logger.warning(f"Lỗi khi sử dụng GPT-4 với response_format, thử lại với GPT-3.5: {api_error}")
            
            # Điều chỉnh prompt để yêu cầu rõ ràng hơn về định dạng JSON
            prompt += """
            Hãy trả về kết quả CHÍNH XÁC theo định dạng sau:
            ```json
            {
                "urls": [
                    "https://example.com/job/1",
                    "https://example.com/job/2",
                    ...
                ]
            }
            ```
            """
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý AI chuyên tìm kiếm việc làm. Bạn có khả năng thực hiện tìm kiếm thông minh và trả về kết quả dưới dạng JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            # Phân tích kết quả JSON từ văn bản
            result = response.choices[0].message.content
            
            # Trích xuất phần JSON từ văn bản
            try:
                # Tìm định dạng JSON trong văn bản kết quả
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    job_urls = data.get("urls", [])
                else:
                    # Cố gắng tìm danh sách URLs trong văn bản
                    urls = re.findall(rf'{base_url}/[\w-]+/[\w-]+', result)
                    if urls:
                        job_urls = urls
                    else:
                        # Nếu không tìm thấy, tạo danh sách giả lập
                        logger.warning("Không thể trích xuất URLs từ kết quả, tạo danh sách giả lập")
                        job_urls = [
                            f"{base_url}/tim-kiem-viec-lam-nhanh?q={keyword.replace(' ', '+')}"
                            for keyword in keywords
                        ]
            except Exception as json_error:
                logger.error(f"Lỗi khi phân tích JSON từ kết quả: {json_error}")
                # Tạo danh sách giả lập nếu không thể phân tích JSON
                job_urls = [
                    f"{base_url}/tim-kiem-viec-lam-nhanh?q={keyword.replace(' ', '+')}"
                    for keyword in keywords
                ]
        
        # Kiểm tra và chỉnh sửa URL nếu cần
        validated_urls = []
        for url in job_urls:
            # Đảm bảo URL hợp lệ và bắt đầu bằng base_url
            if isinstance(url, str) and url.startswith(base_url):
                validated_urls.append(url)
        
        logger.info(f"Đã tìm thấy {len(validated_urls)} URLs việc làm phù hợp")
        return validated_urls
    except Exception as e:
        logger.error(f"Lỗi khi sử dụng OpenAI API để tìm kiếm việc làm: {e}")
        # Trả về danh sách trống và sử dụng phương pháp tìm kiếm truyền thống
        return []

def generate_cv_with_openai(user_info, job_info):
    """
    Sử dụng OpenAI để tạo nội dung CV dựa trên thông tin người dùng và công việc
    
    Args:
        user_info (dict): Thông tin cá nhân của người dùng
        job_info (dict): Thông tin về công việc đang ứng tuyển
        
    Returns:
        str: Nội dung CV được tạo
    """
    try:
        # Tạo prompt cho OpenAI
        prompt = f"""
        Tạo một CV chuyên nghiệp dựa trên thông tin sau:
        
        THÔNG TIN CÁ NHÂN:
        {user_info}
        
        THÔNG TIN CÔNG VIỆC ĐANG ỨNG TUYỂN:
        {job_info}
        
        Hãy tạo một CV đầy đủ, chuyên nghiệp và phù hợp với công việc đang ứng tuyển.
        CV nên bao gồm các phần:
        1. Thông tin cá nhân
        2. Mục tiêu nghề nghiệp
        3. Học vấn
        4. Kinh nghiệm làm việc
        5. Kỹ năng
        6. Chứng chỉ (nếu có)
        7. Hoạt động ngoại khóa (nếu có)
        8. Sở thích (tùy chọn)
        
        Hãy tối ưu hóa CV để phù hợp với yêu cầu của công việc đang ứng tuyển.
        """
        
        logger.info("Gọi OpenAI API để tạo nội dung CV")
        
        # Gọi OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Sử dụng GPT-3.5 thay vì GPT-4 để tránh lỗi
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia tư vấn nghề nghiệp và viết CV. Nhiệm vụ của bạn là tạo CV chuyên nghiệp, hấp dẫn và phù hợp với công việc mà người dùng đang ứng tuyển."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Lấy nội dung CV
        cv_content = response.choices[0].message.content
        logger.info("Đã tạo nội dung CV thành công")
        
        return cv_content
    except Exception as e:
        logger.error(f"Lỗi khi sử dụng OpenAI API để tạo CV: {e}")
        return f"Không thể tạo CV. Lỗi: {e}" 