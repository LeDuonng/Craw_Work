"""
Ví dụ cụ thể về cách OpenAI Deep Search hoạt động
File này chỉ để minh họa và học tập
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()

# Khởi tạo OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_jobs_with_traditional_search(keywords, base_url):
    """
    Tìm kiếm việc làm theo cách truyền thống, ghép từ khóa vào URL
    
    Args:
        keywords (list): Danh sách từ khóa
        base_url (str): URL cơ sở của trang web việc làm
        
    Returns:
        list: Danh sách các URL việc làm theo cách truyền thống
    """
    # Giả lập quá trình tìm kiếm truyền thống
    traditional_urls = []
    
    for keyword in keywords:
        # Giả lập URL tìm kiếm truyền thống
        search_url = f"{base_url}/tim-kiem-viec-lam-nhanh?q={keyword.replace(' ', '+')}"
        
        # Giả lập kết quả trả về
        traditional_urls.append(f"{base_url}/viec-lam/1234-{keyword.replace(' ', '-')}")
        traditional_urls.append(f"{base_url}/viec-lam/5678-{keyword.replace(' ', '-')}-senior")
    
    return traditional_urls

def get_jobs_with_deep_search(keywords, base_url):
    """
    Tìm kiếm việc làm với OpenAI Deep Search
    
    Args:
        keywords (list): Danh sách từ khóa
        base_url (str): URL cơ sở của trang web việc làm
        
    Returns:
        list: Danh sách các URL việc làm thông qua OpenAI Deep Search
    """
    # Tạo prompt cho OpenAI
    keywords_str = ", ".join(keywords)
    
    prompt = f"""
    Bạn là trợ lý AI chuyên tìm kiếm việc làm. Hãy phân tích những từ khóa sau đây:
    
    {keywords_str}
    
    Và đề xuất danh sách các công việc liên quan, bao gồm:
    1. Công việc chứa chính xác từ khóa
    2. Công việc tương tự nhưng có thể không chứa chính xác từ khóa
    3. Công việc liên quan đến kỹ năng và lĩnh vực của từ khóa
    
    Với mỗi công việc, hãy tạo một URL giả định bắt đầu bằng {base_url}
    Trả về dưới dạng mảng JSON với ít nhất 10 URL.
    """
    
    # Gọi OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý AI chuyên tìm kiếm việc làm."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    # Phân tích kết quả JSON
    result = response.choices[0].message.content
    jobs_data = json.loads(result)
    
    # Trả về danh sách URL
    return jobs_data.get("urls", [])

def compare_search_results():
    """
    So sánh kết quả giữa tìm kiếm truyền thống và OpenAI Deep Search
    """
    # Thiết lập dữ liệu mẫu
    keywords = ["Python Developer", "Data Analyst"]
    base_url = "https://www.vietnamworks.com"
    
    # Tìm kiếm theo cách truyền thống
    print("===== Kết quả tìm kiếm truyền thống =====")
    traditional_results = get_jobs_with_traditional_search(keywords, base_url)
    for url in traditional_results:
        print(url)
    
    print("\n===== Kết quả tìm kiếm với OpenAI Deep Search =====")
    deep_search_results = get_jobs_with_deep_search(keywords, base_url)
    for url in deep_search_results:
        print(url)
    
    # So sánh kết quả
    print("\n===== So sánh kết quả =====")
    print(f"Số lượng kết quả tìm kiếm truyền thống: {len(traditional_results)}")
    print(f"Số lượng kết quả tìm kiếm với OpenAI Deep Search: {len(deep_search_results)}")
    
    # Tìm các URL giống nhau
    common_urls = set(traditional_results).intersection(set(deep_search_results))
    print(f"Số lượng kết quả giống nhau: {len(common_urls)}")
    
    # Các URL duy nhất trong OpenAI Deep Search
    unique_deep_search = set(deep_search_results).difference(set(traditional_results))
    print(f"Số lượng kết quả duy nhất từ OpenAI Deep Search: {len(unique_deep_search)}")
    print("\nMột số kết quả duy nhất từ OpenAI Deep Search:")
    for url in list(unique_deep_search)[:5]:  # Hiển thị tối đa 5 URL
        print(url)

def main():
    """
    Hàm chính
    """
    compare_search_results()

if __name__ == "__main__":
    main() 