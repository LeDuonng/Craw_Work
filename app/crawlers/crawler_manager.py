"""
Crawler Manager - Quản lý tất cả các crawler
"""
import threading
import pandas as pd
import time
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from app.utils.config import MAX_THREADS, JOB_LINKS_FILE, JOB_DETAILS_FILE
from app.crawlers.vietnamworks_crawler import VietnamWorksCrawler

# Thiết lập logger
logger = logging.getLogger(__name__)

class CrawlerManager:
    """
    Quản lý tất cả các crawler và điều phối quá trình crawl
    """
    
    def __init__(self):
        """
        Khởi tạo CrawlerManager với các crawler được hỗ trợ
        """
        self.crawlers = {
            'VietnamWorks': VietnamWorksCrawler(),
            # Thêm các crawler khác ở đây khi cần
        }
        
        self.job_links = []
        self.job_details = []
        
        # Cờ để kiểm soát quá trình crawl
        self.pause_flag = threading.Event()
        self.pause_flag.set()  # Mặc định là không tạm dừng
        
        # Biến để theo dõi tiến trình
        self.total_links = 0
        self.processed_links = 0
        self.total_details = 0
        self.processed_details = 0
        
        # Callback functions
        self.on_link_crawled = None
        self.on_detail_crawled = None
        self.on_progress_updated = None
        
        # Chế độ tìm kiếm
        self.deep_search_mode = True  # Mặc định sử dụng OpenAI Deep Search
        
        logger.info("Crawler Manager đã được khởi tạo với chế độ OpenAI Deep Search")
    
    def set_callbacks(self, on_link_crawled=None, on_detail_crawled=None, on_progress_updated=None):
        """
        Thiết lập các hàm callback
        
        Args:
            on_link_crawled (function): Được gọi khi một link được crawl
            on_detail_crawled (function): Được gọi khi chi tiết của một công việc được crawl
            on_progress_updated (function): Được gọi khi tiến trình thay đổi
        """
        self.on_link_crawled = on_link_crawled
        self.on_detail_crawled = on_detail_crawled
        self.on_progress_updated = on_progress_updated
    
    def set_search_mode(self, use_deep_search=True):
        """
        Thiết lập chế độ tìm kiếm
        
        Args:
            use_deep_search (bool): True để sử dụng OpenAI Deep Search, False để sử dụng tìm kiếm truyền thống
        """
        self.deep_search_mode = use_deep_search
        logger.info(f"Đã chuyển sang chế độ {'OpenAI Deep Search' if use_deep_search else 'tìm kiếm truyền thống'}")
    
    def pause_crawling(self):
        """
        Tạm dừng quá trình crawl
        """
        self.pause_flag.clear()
        logger.info("Đã tạm dừng quá trình crawl")
    
    def resume_crawling(self):
        """
        Tiếp tục quá trình crawl
        """
        self.pause_flag.set()
        logger.info("Đã tiếp tục quá trình crawl")
    
    def crawl_job_links(self, keywords, location=None, filters=None, limit=None):
        """
        Crawl các link việc làm từ tất cả các trang web được hỗ trợ
        
        Args:
            keywords (list): Danh sách từ khóa tìm kiếm
            location (dict, optional): Thông tin vị trí địa lý
            filters (dict, optional): Các bộ lọc bổ sung
            limit (int, optional): Giới hạn số lượng link
            
        Returns:
            list: Danh sách các URL việc làm
        """
        self.job_links = []
        self.total_links = 0
        self.processed_links = 0
        
        logger.info(f"Bắt đầu crawl link việc làm với {len(keywords)} từ khóa: {', '.join(keywords)}")
        logger.info(f"Chế độ tìm kiếm: {'OpenAI Deep Search' if self.deep_search_mode else 'Tìm kiếm truyền thống'}")
        
        # Tạo thread cho mỗi crawler
        threads = []
        for crawler_name, crawler in self.crawlers.items():
            thread = threading.Thread(
                target=self._crawl_links_from_site,
                args=(crawler, keywords, location, filters, limit)
            )
            threads.append(thread)
            thread.start()
        
        # Chờ tất cả các thread hoàn thành
        for thread in threads:
            thread.join()
        
        # Lưu danh sách link vào file CSV
        self._save_links_to_csv()
        
        logger.info(f"Hoàn thành crawl link việc làm, tìm thấy {len(self.job_links)} kết quả")
        
        return self.job_links
    
    def _crawl_links_from_site(self, crawler, keywords, location, filters, limit):
        """
        Crawl các link việc làm từ một trang web cụ thể
        
        Args:
            crawler (BaseCrawler): Crawler cụ thể
            keywords (list): Danh sách từ khóa tìm kiếm
            location (dict, optional): Thông tin vị trí địa lý
            filters (dict, optional): Các bộ lọc bổ sung
            limit (int, optional): Giới hạn số lượng link
        """
        try:
            # Crawl các link việc làm
            links = crawler.search_jobs(keywords, location, filters)
            
            # Giới hạn số lượng link nếu cần
            if limit and len(links) > limit:
                links = links[:limit]
                logger.info(f"Đã giới hạn kết quả từ {crawler.name} xuống {limit} link")
            
            # Cập nhật tổng số link
            with threading.Lock():
                self.total_links += len(links)
                logger.debug(f"Tìm thấy {len(links)} link từ {crawler.name}")
                
                # Thêm vào danh sách chung
                for link in links:
                    # Kiểm tra cờ tạm dừng
                    self.pause_flag.wait()
                    
                    self.job_links.append({
                        'url': link,
                        'source': crawler.name,
                        'status': 'Đang chờ'
                    })
                    
                    self.processed_links += 1
                    
                    # Gọi callback nếu có
                    if self.on_link_crawled:
                        self.on_link_crawled(link, crawler.name)
                    
                    # Cập nhật tiến trình
                    if self.on_progress_updated:
                        progress = (self.processed_links / self.total_links) * 100 if self.total_links > 0 else 0
                        self.on_progress_updated('links', progress)
        
        except Exception as e:
            logger.error(f"Lỗi khi crawl link từ {crawler.name}: {e}")
            print(f"Lỗi khi crawl link từ {crawler.name}: {e}")
    
    def _save_links_to_csv(self):
        """
        Lưu danh sách link vào file CSV
        """
        try:
            df = pd.DataFrame(self.job_links)
            df.to_csv(JOB_LINKS_FILE, index=False)
            logger.info(f"Đã lưu {len(self.job_links)} link vào {JOB_LINKS_FILE}")
            print(f"Đã lưu {len(self.job_links)} link vào {JOB_LINKS_FILE}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu file CSV: {e}")
            print(f"Lỗi khi lưu file CSV: {e}")
    
    def crawl_job_details(self, links=None):
        """
        Crawl chi tiết việc làm từ danh sách link
        
        Args:
            links (list, optional): Danh sách link cần crawl. Nếu None, sẽ đọc từ file CSV
            
        Returns:
            list: Danh sách thông tin chi tiết việc làm
        """
        self.job_details = []
        self.processed_details = 0
        
        # Nếu không có links, đọc từ file CSV
        if not links:
            try:
                if os.path.exists(JOB_LINKS_FILE):
                    df = pd.read_csv(JOB_LINKS_FILE)
                    links = df.to_dict('records')
                    logger.info(f"Đã đọc {len(links)} link từ file {JOB_LINKS_FILE}")
                else:
                    logger.warning(f"File {JOB_LINKS_FILE} không tồn tại")
                    print(f"File {JOB_LINKS_FILE} không tồn tại")
                    return []
            except Exception as e:
                logger.error(f"Lỗi khi đọc file CSV: {e}")
                print(f"Lỗi khi đọc file CSV: {e}")
                return []
        
        self.total_details = len(links)
        logger.info(f"Bắt đầu crawl chi tiết cho {self.total_details} link việc làm")
        
        # Sử dụng ThreadPoolExecutor để crawl đa luồng
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # Submit các task
            futures = [executor.submit(self._crawl_job_detail, link) for link in links]
            
            # Xử lý kết quả khi hoàn thành
            for future in futures:
                # Kiểm tra cờ tạm dừng
                self.pause_flag.wait()
                
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Lỗi khi crawl chi tiết: {e}")
                    print(f"Lỗi khi crawl chi tiết: {e}")
        
        # Lưu chi tiết vào file CSV
        self._save_details_to_csv()
        
        logger.info(f"Hoàn thành crawl chi tiết, đã xử lý {self.processed_details}/{self.total_details} link")
        
        return self.job_details
    
    def _crawl_job_detail(self, link_info):
        """
        Crawl chi tiết của một việc làm
        
        Args:
            link_info (dict): Thông tin về link việc làm
        """
        try:
            url = link_info['url']
            source = link_info['source']
            
            # Lấy crawler tương ứng
            crawler = self.crawlers.get(source)
            if not crawler:
                logger.warning(f"Không tìm thấy crawler cho {source}")
                print(f"Không tìm thấy crawler cho {source}")
                return
            
            logger.debug(f"Đang crawl chi tiết từ {url}")
            
            # Crawl chi tiết
            job_detail = crawler.extract_job_details(url)
            
            if job_detail:
                # Thêm thông tin nguồn và URL
                job_detail['source'] = source
                job_detail['url'] = url
                
                # Thêm vào danh sách chung
                with threading.Lock():
                    self.job_details.append(job_detail)
                    self.processed_details += 1
                    
                    # Gọi callback nếu có
                    if self.on_detail_crawled:
                        self.on_detail_crawled(job_detail)
                    
                    # Cập nhật tiến trình
                    if self.on_progress_updated:
                        progress = (self.processed_details / self.total_details) * 100 if self.total_details > 0 else 0
                        self.on_progress_updated('details', progress)
                
                # Cập nhật trạng thái
                link_info['status'] = 'Đã crawl chi tiết'
                logger.debug(f"Đã crawl xong chi tiết cho {url}")
            else:
                # Cập nhật trạng thái
                link_info['status'] = 'Lỗi'
                logger.warning(f"Không thể lấy chi tiết từ {url}")
        
        except Exception as e:
            logger.error(f"Lỗi khi crawl chi tiết từ {link_info['url']}: {e}")
            print(f"Lỗi khi crawl chi tiết từ {link_info['url']}: {e}")
            # Cập nhật trạng thái
            link_info['status'] = 'Lỗi'
    
    def _save_details_to_csv(self):
        """
        Lưu chi tiết việc làm vào file CSV
        """
        try:
            df = pd.DataFrame(self.job_details)
            df.to_csv(JOB_DETAILS_FILE, index=False)
            logger.info(f"Đã lưu {len(self.job_details)} chi tiết việc làm vào {JOB_DETAILS_FILE}")
            print(f"Đã lưu {len(self.job_details)} chi tiết việc làm vào {JOB_DETAILS_FILE}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu file CSV: {e}")
            print(f"Lỗi khi lưu file CSV: {e}")
    
    def get_progress(self, task_type):
        """
        Lấy tiến trình hiện tại
        
        Args:
            task_type (str): Loại task ('links' hoặc 'details')
            
        Returns:
            float: Phần trăm tiến trình
        """
        if task_type == 'links':
            return (self.processed_links / self.total_links) * 100 if self.total_links > 0 else 0
        elif task_type == 'details':
            return (self.processed_details / self.total_details) * 100 if self.total_details > 0 else 0
        return 0 