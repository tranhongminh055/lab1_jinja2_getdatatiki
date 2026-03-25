# ===== PHẦN 1: IMPORT CÁC THƯ VIỆN CẦN THIẾT =====
# Dùng để mã hóa từ khóa tìm kiếm thành URL-safe string (ví dụ: "điện thoại" -> "di%E1%BB%87n%20tho%E1%BA%A1i")
from urllib.parse import quote
# Nhập Flask để tạo web app, render_template để hiển thị HTML, request để lấy dữ liệu từ form
from flask import Flask, render_template, request
# Nhập webdriver từ Selenium để điều khiển trình duyệt Chrome tự động
from selenium import webdriver
# Nhập By để tìm phần tử HTML (bằng CSS selector, XPath, ID, etc.)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Tự động tải ChromeDriver phù hợp với version Chrome hiện tại
from webdriver_manager.chrome import ChromeDriverManager
# Cấu hình dịch vụ ChromeDriver (chỉ định đường dẫn driver)
from selenium.webdriver.chrome.service import Service
# Cấu hình các tùy chọn cho Chrome (headless, disable GPU, etc.)
from selenium.webdriver.chrome.options import Options
# Nhập các module hệ thống: os (quản lý file/folder), shutil (xóa folder), time (delay), logging (ghi log)
import os, shutil, time, logging

# ===== PHẦN 2: KHỞI TẠO ỨNG DỤNG FLASK =====
# Tạo instance Flask - đây là ứng dụng web chính
app = Flask(__name__)

# ===== CẤU HÌNH HỆ THỐNG GHI NHẬT KÝ =====
# Cấu hình logging: 
#   - level=logging.INFO: chỉ hiển thị INFO và các level cao hơn (WARNING, ERROR, CRITICAL)
#   - format: hiển thị thời gian [%(asctime)s], level log [%(levelname)s], và nội dung %(message)s
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# ===== PHẦN 3: HÀM KHỞI TẠO CHROME DRIVER =====
def init_chrome_driver():
    # Docstring: mô tả hàm này làm gì
    """Khởi tạo Chrome webdriver với cấu hình headless"""
    
    # Lấy đường dẫn đến thư mục cache WebDriver Manager (~/.wdm) - thư mục lưu ChromeDriver đã tải
    cache_path = os.path.expanduser("~/.wdm")
    
    # Kiểm tra xem thư mục cache có tồn tại không
    if os.path.exists(cache_path):
        # Thử xóa toàn bộ thư mục cache cũ
        try:
            shutil.rmtree(cache_path)
        # Nếu xóa lỗi, bỏ qua và tiếp tục (không dừng chương trình)
        except Exception:
            pass

    # Tạo đối tượng Options để cấu hình Chrome
    options = Options()
    # Chế độ headless: Chrome chạy nền mà không hiển thị giao diện đồ họa
    options.add_argument("--headless=new")
    # Tắt GPU acceleration (không cần GPU khi headless)
    options.add_argument("--disable-gpu")
    # Vô hiệu hoá các tính năng không cần thiết để giảm tải và log
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-features=PushMessaging")
    options.add_argument("--disable-global-keyed-logging")
    options.add_argument("--disable-gcm")
    # Tắt sandbox security (cho phép Selenium chạy trong container/environment hạn chế)
    options.add_argument("--no-sandbox")
    # Tắt /dev/shm (shared memory) - tránh lỗi khi memory không đủ
    options.add_argument("--disable-dev-shm-usage")
    # Đặt kích thước cửa sổ là 1920x1080 pixels
    options.add_argument("--window-size=1920,1080")
    # Giấu User-Agent thật của Chrome, giả mạo thành Chrome thực (tránh bị detect là bot)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # Khối try-except: bắt lỗi khi khởi tạo Chrome
    try:
        # Tự động tải ChromeDriver phù hợp từ internet (nếu chưa có)
        driver_path = ChromeDriverManager().install()
        # Tạo Service object với đường dẫn ChromeDriver
        service = Service(driver_path)
        # Khởi tạo Chrome webdriver với service (driver path) và options (cấu hình)
        driver = webdriver.Chrome(service=service, options=options)
        # Đặt timeout mặc định: chờ tối đa 5 giây khi tìm phần tử trên trang
        driver.implicitly_wait(5)
        # Ghi log thông báo khởi động Chrome thành công
        logging.info("Chrome khởi động thành công")
        # Trả về driver để sử dụng
        return driver
    # Bắt lỗi nếu có vấn đề
    except Exception as e:
        # Ghi log đầy đủ lỗi (stack trace)
        logging.exception("Lỗi khởi động Chrome")
        # Ném lại exception để hàm gọi biết đã có lỗi
        raise

# ===== PHẦN 4: HÀM LẤY DỮ LIỆU TỪ TIKI =====
def get_tiki_data(keyword="điện thoại"):
    # Docstring: mô tả hàm này làm gì, tham số mặc định là "điện thoại"
    """Lấy dữ liệu sản phẩm từ Tiki bằng Selenium"""
    
    # Gọi hàm init_chrome_driver() để khởi tạo Chrome driver
    driver = init_chrome_driver()
    
    # Khối try-except lớn: bắt lỗi trong toàn bộ hàm
    try:
        # Tạo URL với từ khóa được mã hóa (ví dụ: search?q=di%E1%BB%87n%20tho%E1%BA%A1i)
        url = f"https://tiki.vn/search?q={quote(keyword)}"
        # Mở URL này trong Chrome
        driver.get(url)
        logging.info(f"Tải trang Tiki để tìm '{keyword}' thành công")

        # Dùng WebDriverWait thay vì sleep cố định để tăng tốc và linh hoạt
        wait = WebDriverWait(driver, 5)
        # Chờ phần tử đầu tiên hiển thị (trong tối đa 5 giây)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-view-index], div.product-item, .ProductItem, a[href*="product"]')))
        except Exception:
            # nếu không tìm nhanh, vẫn tiếp tục; không dừng để tránh fail tổng thể
            pass

        # Cuộn tẹo để kích hoạt lazy-load (nếu cần) nhưng hạn chế
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        except Exception:
            pass

        # Dừng một chút để render xong, thời gian ngắn hơn
        time.sleep(0.7)

        # Danh sách các CSS selector để tìm sản phẩm (thử lần lượt nếu selector trước không có)
        selectors = [
            'div[data-view-index]',      # Tiki's product items with data-view-index
            'div.product-item',          # Product items with class product-item
            'div[class*="product"]',     # Any div containing 'product' in class name
            '.ProductItem',              # ProductItem class
            'a[href*="product"]'         # Links containing 'product' in href
        ]
        
        # Khởi tạo danh sách rỗng để lưu phần tử sản phẩm tìm được
        products = []
        # Lặp qua từng selector
        for sel in selectors:
            # Cố gắng tìm phần tử sản phẩm bằng selector này
            try:
                # Tìm tất cả phần tử khớp với selector (trả về list)
                found = driver.find_elements(By.CSS_SELECTOR, sel)
                # Nếu tìm thấy ít nhất một phần tử
                if found:
                    # Gán danh sách phần tử vào products
                    products = found
                    # Ghi log số phần tử tìm được
                    logging.info(f"Tiki: Tìm thấy {len(found)} sản phẩm")
                    # Thoát khỏi vòng lặp vì đã tìm được
                    break
            # Nếu selector này không hoạt động, tiếp tục sang selector tiếp theo
            except: 
                continue

        # Khởi tạo danh sách rỗng để lưu dữ liệu sản phẩm đã trích xuất
        data = []
        # Kiểm tra xem có tìm thấy sản phẩm không
        if not products:
            # Ghi log cảnh báo không tìm thấy
            logging.warning("Không tìm thấy sản phẩm trên Tiki")
            # Đóng Chrome driver để giải phóng tài nguyên
            driver.quit()
            # Trả về danh sách rỗng
            return []

        # Lặp qua tối đa 10 sản phẩm đầu tiên (products[:10])
        for product in products[:10]:
            # Khối try-except: bắt lỗi khi xử lý mỗi sản phẩm
            try:
                # Khởi tạo các biến lưu thông tin sản phẩm (mặc định là chuỗi rỗng)
                title, price, img, link = '', '', '', ''
                
                # ===== TRÍCH XUẤT TÊN SẢN PHẨM =====
                # Cố gắng lấy tên từ h2 hoặc thẻ a có attribute title
                try:
                    # Tìm h2 hoặc a có attribute title (thử cả 2)
                    title = product.find_element(By.XPATH, ".//h2 | .//a[@title]").text
                # Nếu lỗi, thử cách khác
                except:
                    # Cố gắng lấy attribute 'title' từ thẻ a, nếu không có thì lấy text của a
                    try:
                        title = product.find_element(By.XPATH, ".//a[@href]").get_attribute('title') or product.find_element(By.XPATH, ".//a[@href]").text
                    # Nếu cách này cũng lỗi, bỏ qua (title vẫn là '')
                    except: 
                        pass

                # ===== TRÍCH XUẤT GIÁ SẢN PHẨM =====
                # Cố gắng lấy giá từ span có class chứa 'price'
                try:
                    price = product.find_element(By.XPATH, ".//span[@class*='price']").text
                # Nếu lỗi, bỏ qua (price vẫn là '')
                except: 
                    pass

                # ===== TRÍCH XUẤT HÌNH ẢNH =====
                # Cố gắng lấy src hoặc data-src của thẻ img
                try:
                    # Lấy src (nếu có), nếu không có thì lấy data-src (lazy-load images)
                    img = product.find_element(By.CSS_SELECTOR, 'img').get_attribute('src') or product.find_element(By.CSS_SELECTOR, 'img').get_attribute('data-src')
                # Nếu lỗi, bỏ qua (img vẫn là '')
                except: 
                    pass

                # ===== TRÍCH XUẤT LINK SẢN PHẨM =====
                # Cố gắng lấy href (link) từ thẻ a đầu tiên
                try:
                    link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    # Nếu link là đường dẫn tương đối (không bắt đầu bằng http), thêm domain Tiki vào
                    if link and not link.startswith('http'):
                        link = 'https://tiki.vn' + link
                # Nếu lỗi, bỏ qua (link vẫn là '')
                except: 
                    pass

                # Kiểm tra xem có dữ liệu hợp lệ không (phải có tiêu đề và hình ảnh hoặc giá)
                if title and (img or price):
                    # Thêm sản phẩm vào danh sách với:
                    data.append({
                        # Tên sản phẩm (hoặc 'N/A' nếu không có)
                        'title': title,
                        # Giá (hoặc 'N/A' nếu không có)
                        'price': price or 'N/A',
                        # Ảnh (hoặc placeholder image nếu không có)
                        'img': img or 'https://via.placeholder.com/200',
                        # Link (hoặc '#' nếu không có)
                        'link': link or '#'
                    })
            # Nếu xảy ra lỗi khi xử lý sản phẩm này, tiếp tục sang sản phẩm tiếp theo
            except: 
                continue

        # Đóng Chrome driver (quan trọng để giải phóng tài nguyên)
        driver.quit()
        # Ghi log thông báo đã thu thập xong
        logging.info(f"Tiki: Thu thập {len(data)} sản phẩm thành công")
        # Trả về danh sách dữ liệu sản phẩm
        return data

    # Nếu có exception trong toàn bộ khối try, bắt tại đay
    except Exception as e:
        # Đóng Chrome driver
        driver.quit()
        # Ghi log đầy đủ lỗi (stack trace)
        logging.exception("Lỗi Tiki")
        # Trả về danh sách rỗng khi có lỗi
        return []

# ===== PHẦN 5: ROUTE CHÍNH =====
# Decorator: định nghĩa route "/" xử lý 2 phương thức GET (mở trang) và POST (submit form)
@app.route("/", methods=["GET", "POST"])
def home():
    # Docstring
    """Trang chủ Tiki Scraper"""
    
    # Khởi tạo biến keyword với giá trị mặc định
    keyword = "điện thoại"
    # Khởi tạo danh sách sản phẩm rỗng
    products = []
    # Khởi tạo biến thông báo (None = không có thông báo)
    notice = None

    # Kiểm tra xem request phương thức POST (form được submit)
    if request.method == "POST":
        # Lấy value của input "keyword" từ form, mặc định là "điện thoại", sau đó loại bỏ khoảng trắng thừa
        keyword = request.form.get("keyword", "điện thoại").strip()
        # Ghi log từ khóa tìm kiếm
        logging.info(f"Tìm kiếm: '{keyword}' trên Tiki")

        # Khối try-except: bắt lỗi khi gọi hàm lấy dữ liệu
        try:
            # Gọi hàm get_tiki_data() để lấy dữ liệu sản phẩm từ Tiki
            products = get_tiki_data(keyword)
            # Nếu không có sản phẩm
            if not products:
                # Gán thông báo cho người dùng
                notice = f"Không tìm thấy sản phẩm. Thử từ khóa khác!"
        # Bắt exception nếu có lỗi
        except Exception as e:
            # Ghi log đầy đủ lỗi
            logging.exception("Lỗi khi tìm kiếm")
            # Gán thông báo lỗi cho người dùng
            notice = f"Lỗi: {str(e)}"

    # Render template index.html với dữ liệu:
    return render_template("index.html", 
                         # Danh sách sản phẩm (có thể rỗng)
                         products=products, 
                         # Thông báo cho người dùng (có thể None)
                         notice=notice, 
                         # Từ khóa tìm kiếm (hiển thị lại trong input)
                         keyword=keyword)

# ===== PHẦN 6: ĐIỂM VÀO CHƯƠNG TRÌNH =====
# Kiểm tra xem file này có phải được chạy trực tiếp không (không phải import từ file khác)
if __name__ == "__main__":
    # Ghi log thông báo khởi động ứng dụng
    logging.info("Khởi động Tiki Web Scraper...")
    # Ghi log hướng dẫn truy cập
    logging.info("Truy cập http://localhost:5000")
    # Chạy Flask app với:
    #   debug=True: tự động reload khi code thay đổi
    #   host='localhost': chỉ cho phép truy cập từ máy local (127.0.0.1)
    #   port=5000: cổng mặc định của Flask
    app.run(debug=True, host='localhost', port=5000)
