# CrawWork - Ứng dụng Tìm việc và Tạo CV Tự động

CrawWork là một ứng dụng desktop được phát triển bằng Python, giúp người dùng tìm kiếm cơ hội việc làm từ nhiều trang tuyển dụng uy tín và tạo CV chuyên nghiệp một cách tự động.

## Tính năng chính

### Module Tìm việc
- Crawl dữ liệu tuyển dụng từ các trang uy tín (VietnamWorks, TopCV, CareerViet, JobsGO, CareerLink, Timviecnhanh, JobStreet, Glints, ITviec, 123Job)
- Lọc, làm sạch và chuẩn hóa dữ liệu theo nhiều tiêu chí
- Sắp xếp kết quả theo khoảng cách địa lý, mức lương, kinh nghiệm...
- Xuất dữ liệu ra file CSV

### Module Tạo CV
- Nhập thông tin cá nhân, kinh nghiệm và học vấn
- Tự động soạn thảo nội dung CV với sự hỗ trợ của OpenAI
- Xuất CV ra file PDF hoặc Word
- Tích hợp Google Maps để chọn vị trí

## Yêu cầu hệ thống
- Python 3.x
- Các thư viện được liệt kê trong file requirements.txt

## Cài đặt

1. Clone repository:
```
git clone https://github.com/yourusername/crawwork.git
cd crawwork
```

2. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

3. Tạo file .env từ file .env và cập nhật các khóa API:
```
cp .env
```

4. Chạy ứng dụng:
```
python src/main.py
```

## Hướng dẫn sử dụng

### Module Tìm việc
1. Nhập từ khóa công việc cần tìm
2. Chọn vị trí hiện tại của bạn (thông qua Google Maps)
3. Chọn các tiêu chí lọc (địa điểm, kinh nghiệm, mức lương...)
4. Nhấn "Crawl Link Tuyển Dụng" để lấy danh sách link
5. Nhấn "Crawl Dữ Liệu Chi Tiết & Xuất CSV" để lấy thông tin chi tiết

### Module Tạo CV
1. Nhập thông tin cá nhân và nghề nghiệp
2. Tải lên ảnh cá nhân (nếu cần)
3. Nhấn "Tạo CV" để xử lý nội dung
4. Nhấn "Xuất CV" để lưu file PDF hoặc Word

## Đóng góp
Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request.
