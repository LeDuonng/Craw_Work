# Ứng Dụng Cào Dữ Liệu Tuyển Dụng Việc Làm Thông Minh & Tạo CV Tự Động

## Giới thiệu

Ứng dụng này giúp người dùng tự động tìm kiếm việc làm từ nhiều trang web tuyển dụng uy tín, tổng hợp và lọc dữ liệu theo các tiêu chí tùy chỉnh, đồng thời hỗ trợ tạo CV chuyên nghiệp bằng AI. Ứng dụng cung cấp giao diện đồ họa trực quan, thân thiện với người dùng, phù hợp với mọi đối tượng.

## Tính năng chính

1. **Tìm việc thông minh với OpenAI Deep Search**:
   - Sử dụng OpenAI để phân tích ngữ nghĩa và tìm kiếm thông minh
   - Tự động thu thập dữ liệu tuyển dụng từ các trang web việc làm uy tín
   - Tìm kiếm theo nhiều từ khóa và tiêu chí, vượt xa phương pháp tìm kiếm truyền thống
   - Hiểu ngữ cảnh và ý định tìm kiếm của người dùng thay vì chỉ ghép từ khóa vào URL

2. **Xử lý & Sắp xếp nâng cao**:
   - Lọc, làm sạch, chuẩn hóa dữ liệu theo các tiêu chí tùy chỉnh
   - Hiển thị kết quả theo từng bước cào
   - Tối ưu hóa kết quả tìm kiếm nhờ công nghệ AI

3. **Tạo CV chuyên nghiệp**:
   - Sử dụng OpenAI để soạn thảo nội dung CV chuyên nghiệp
   - Xuất ra định dạng PDF hoặc Word
   - Tùy chỉnh CV theo yêu cầu công việc cụ thể

4. **Trải nghiệm người dùng tối ưu**:
   - Giao diện trực quan, thân thiện, dễ sử dụng
   - Có thể tạm dừng/tiếp tục quá trình cào
   - Hiển thị dữ liệu theo thời gian thực

## Công nghệ sử dụng

- **OpenAI Deep Search**: Công nghệ tìm kiếm thông minh dựa trên ngữ nghĩa, không chỉ đơn thuần ghép các từ khóa
- **Xử lý ngôn ngữ tự nhiên (NLP)**: Hiểu nhu cầu tìm kiếm của người dùng, phân tích ngữ cảnh
- **Crawling thông minh**: Trích xuất thông tin chính xác từ nhiều nguồn
- **Đa luồng**: Tăng tốc độ xử lý, không block giao diện

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- Các thư viện Python theo file requirements.txt
- API key của OpenAI
- API key của Google Maps (tùy chọn)

### Các bước cài đặt

1. Clone dự án:
   ```
   git clone <URL_repository>
   cd CrawWork
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Tạo file `.env` tại thư mục gốc dự án với nội dung:
   ```
   OPENAI_API_KEY=<your_openai_api_key>
   GOOGLE_MAPS_API_KEY=<your_google_maps_api_key>
   MAX_THREADS=5
   TIMEOUT=30
   USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
   ```

4. Chạy ứng dụng:
   ```
   python main.py
   ```

## Hướng dẫn sử dụng

### Tìm kiếm việc làm

1. **Bước 1: Crawl Link Tuyển Dụng với Tìm Kiếm Thông Minh**
   - Nhập từ khóa công việc cần tìm, ngăn cách bằng dấu phẩy
   - Ứng dụng sẽ sử dụng OpenAI để hiểu ngữ cảnh và ý định tìm kiếm của bạn
   - Chọn địa điểm của bạn (tỉnh/thành phố và quận/huyện)
   - Chọn địa điểm công ty bạn muốn ứng tuyển
   - Thiết lập giới hạn link crawl hoặc chọn "Crawl đến khi hết dữ liệu"
   - Nhấn nút "Bắt đầu Crawl Link Tuyển Dụng"
   - Theo dõi tiến trình và danh sách link đang được crawl
   - Kết quả tìm kiếm sẽ thông minh hơn, liên quan hơn so với tìm kiếm truyền thống

2. **Bước 2: Crawl Dữ Liệu Chi Tiết**
   - Sau khi crawl link xong, nhấn nút "Bước 1 -> Bước 2: Bắt đầu Crawl Dữ Liệu Chi Tiết"
   - OpenAI sẽ giúp phân tích nội dung chi tiết từng trang việc làm
   - Theo dõi tiến trình và dữ liệu chi tiết đang được crawl
   - Bạn có thể tạm dừng quá trình bằng nút "Tạm Dừng Crawl Chi Tiết"

3. **Bước 3: Xuất CSV**
   - Sau khi crawl chi tiết xong, nhấn "Bước 2 -> Bước 3: Xuất CSV"
   - Dữ liệu sẽ được xuất ra file CSV

### Tạo CV tự động

1. **Nhập thông tin cá nhân**
   - Điền đầy đủ thông tin cá nhân, học vấn, kinh nghiệm làm việc, kỹ năng, v.v.
   
2. **Chọn công việc để ứng tuyển**
   - Bạn có thể chọn một công việc từ danh sách việc làm đã crawl ở tab "Tìm Kiếm Việc Làm"
   - Thông tin công việc sẽ hiển thị ở phần "Thông Tin Công Việc Đang Ứng Tuyển"

3. **Tạo CV**
   - Nhập tên file và chọn định dạng (DOCX hoặc PDF)
   - Nhấn nút "Tạo CV"
   - CV sẽ được tạo và lưu vào thư mục app/data/cv_output
   - Bạn có thể xem trước nội dung CV và mở file đã tạo

## Sự khác biệt của tìm kiếm thông minh OpenAI so với tìm kiếm truyền thống

### Tìm kiếm truyền thống
- Chỉ ghép từ khóa vào URL tìm kiếm
- Kết quả phụ thuộc vào từ khóa chính xác
- Không hiểu ngữ cảnh hoặc ý định tìm kiếm
- Dễ bỏ sót các cơ hội việc làm phù hợp

### Tìm kiếm thông minh với OpenAI
- Phân tích ngữ nghĩa và hiểu ý định tìm kiếm
- Tìm kiếm theo ngữ cảnh và mối liên quan
- Kết quả phù hợp hơn, thậm chí khi không chứa từ khóa chính xác
- Khám phá các cơ hội việc làm liên quan mà bạn có thể bỏ qua
- Tiết kiệm thời gian và nâng cao chất lượng kết quả

## Lưu ý quan trọng

- Ứng dụng sử dụng OpenAI API để phân tích dữ liệu, vì vậy cần API key hợp lệ
- Quá trình crawl có thể mất thời gian tùy thuộc vào số lượng trang web và dữ liệu
- Đảm bảo tuân thủ các quy định của trang web về việc crawl dữ liệu

## Xử lý sự cố

- **Lỗi khi khởi động ứng dụng**: Kiểm tra đã cài đặt đầy đủ các thư viện trong requirements.txt chưa
- **Lỗi OpenAI API**: Kiểm tra API key trong file .env
- **Ứng dụng chạy chậm**: Giảm số lượng thread trong file .env
- **Kết quả tìm kiếm không như mong đợi**: Điều chỉnh từ khóa và bộ lọc, đảm bảo thông tin rõ ràng

## Cập nhật

Để cập nhật ứng dụng lên phiên bản mới nhất:

```
git pull
pip install -r requirements.txt
```

## Đóng góp

Nếu có góp ý hoặc phát hiện lỗi, vui lòng tạo issue hoặc pull request trên GitHub.

## Giấy phép

© 2025 LeeDuong. Tất cả các quyền được bảo lưu. 