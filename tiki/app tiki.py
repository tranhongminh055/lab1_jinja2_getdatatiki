# ===== PHẦN 1: IMPORT CÁC THƯ VIỆN CẦN THIẾT =====
# import thu 
from urllib.parse import quote
# Import Flask để tạo ứng dụng web
from flask import Flask, render_template
# Import Selenium để tự động hóa trình duyệt Chrome
from selenium import webdriver
# Import By để tìm kiếm phần tử HTML bằng CSS selector, XPath, v.v.
from selenium.webdriver.common.by import By
# Import ChromeDriverManager để tự động tải ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
# Import Service để cấu hình dịch vụ ChromeDriver
from selenium.webdriver.chrome.service import Service
# Import Options để cấu hình các tùy chọn của Chrome
from selenium.webdriver.chrome.options import Options
# Import os để làm việc với đường dẫn và thư mục hệ thống
import os
# Import shutil để xóa thư mục cache
import shutil
# Import time để tạm dừng chương trình
import time
# Import logging để ghi nhật ký hoạt động
import logging

# PHẦN 2: KHỞI TẠO ỨNG DỤNG FLASK 
# Tạo một ứng dụng Flask với tên là tên của module hiện tại
app = Flask(__name__)

# 3: CẤU HÌNH HỆ THỐNG GHI NHẬT KÝ 
# Đặt mức độ log là INFO, định dạng hiển thị thời gian, mức độ và nội dung
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# 4: ĐỊNH NGHĨA HÀM LẤY DỮ LIỆU TỪ TIKI 
def get_tiki_data(keyword=""):
    # Hàm này có nhiệm vụ lấy dữ liệu sản phẩm từ trang Tiki
    """Lấy dữ liệu sản phẩm từ Tiki bằng Selenium."""
    
    # XÓA CACHE CHROMEDRIVER CŨ 
    # Tạo đường dẫn đến thư mục cache WebDriver Manager (~/.wdm)
    cache_path = os.path.expanduser("~/.wdm")
    # Kiểm tra xem thư mục cache có tồn tại không
    if os.path.exists(cache_path):
        # Nếu tồn tại, thử xóa nó
        try:
            # Xóa toàn bộ thư mục cache và nội dung of it
            shutil.rmtree(cache_path)
        except Exception:
            # Nếu có lỗi khi xóa, bỏ qua và tiếp tục
            pass

    # CẤU HÌNH CHROME OPTIONS 
    # Tạo một đối tượng Options để cấu hình trình duyệt Chrome
    options = Options()
    # Chế độ headless: Chrome chạy mà không hiển thị giao diện (chỉ chạy nội bộ)
    options.add_argument("--headless=new")
    # Tắt GPU acceleration vì chế độ headless không cần nó
    options.add_argument("--disable-gpu")
    # Tắt chế độ sandbox (cho phép Selenium chạy trong môi trường hạn chế)
    options.add_argument("--no-sandbox")
    # Tắt /dev/shm (shared memory) vì nó có thể gây ra vấn đề với Chrome
    options.add_argument("--disable-dev-shm-usage")
    # Đặt kích thước cửa sổ là 1920x1080 pixel
    options.add_argument("--window-size=1920,1080")
    # Đặt User-Agent để giả mạo trình duyệt Chrome thực
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

    # KHỞI TẠO CHROME WEBDRIVER 
    # Khối try-except để bắt lỗi khi khởi tạo Chrome
    try:
        # Tải ChromeDriver từ WebDriver Manager
        driver_path = ChromeDriverManager().install()
        # Tạo một Service object với đường dẫn ChromeDriver
        service = Service(driver_path)
        # Khởi tạo Chrome webdriver với service và options
        driver = webdriver.Chrome(service=service, options=options)
        # Đặt thời gian chờ ngầm định cho tất cả các phần tử là 5 giây
        driver.implicitly_wait(5)
        # Ghi log thông báo Chrome khởi động thành công
        logging.info("Chrome khởi động thành công")
    except Exception as e:
        # Nếu có lỗi, ghi lại lỗi đầy đủ (stack trace)
        logging.exception("Lỗi khởi động Chrome")
        # Ném lại lỗi để hàm gọi biết đã có sự cố
        raise

    #  TRUY CẬP TRANG LAZADA 
    # URL tìm kiếm sản phẩm điện thoại trên Lazada (q=điện%20thoại)
    url = f"https://tiki.vn/search?q={quote(keyword)}"
    # Khối try-except để bắt lỗi khi tải trang
    try:
        # Mở URL trong trình duyệt
        driver.get(url)
        # Ghi log thông báo tải trang thành công
        logging.info("Tải trang Lazada thành công")
    except Exception as e:
        # Nếu có lỗi, đóng trình duyệt
        driver.quit()
        # Ghi log lỗi đầy đủ
        logging.exception("Lỗi tải trang Lazada")
        # Ném lại lỗi
        raise

    #  CHỜ TRANG LOAD DỮ LIỆU ĐỘNG 
    # Chờ 2 giây để trang JavaScript load xong
    time.sleep(2)
    # Khối try-except để bắt lỗi khi cuộn trang
    try:
        # Cuộn xuống cuối trang để load thêm dữ liệu động
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except Exception:
        # Nếu lỗi, bỏ qua và tiếp tục
        pass
    # Chờ thêm 1 giây nữa
    time.sleep(1)

    #  ĐỊNH NGHĨA DANH SÁCH CÁC SELECTOR CSS 
    # Danh sách các CSS selector để tìm phần tử sản phẩm (có dự phòng)
    selectors = [
        '.Bm3ON',  # Selector 1: CSS class .Bm3ON
        'div[data-qa-locator="product-item"]',  # Selector 2: div với attribute data-qa-locator
        'div.sku',  # Selector 3: div với class sku
        'div.c2prKC',  # Selector 4: div với class c2prKC
        'div.product'  # Selector 5: div với class product
    ]

    #  TÌM KIẾM PHẦN TỬ SẢN PHẨM 
    # Khởi tạo danh sách rỗng để lưu trữ phần tử sản phẩm tìm được
    products = []
    # Lặp qua từng selector trong danh sách
    for sel in selectors:
        # Khối try-except để bắt lỗi khi tìm kiếm
        try:
            # Tìm tất cả phần tử khớp với selector hiện tại
            found = driver.find_elements(By.CSS_SELECTOR, sel)
            # Nếu tìm thấy ít nhất một phần tử
            if found:
                # Gán danh sách phần tử tìm được vào biến products
                products = found
                # Ghi log selector và số lượng phần tử tìm được
                logging.info(f"Dùng selector: {sel} → tìm thấy {len(found)} sản phẩm")
                # Thoát vòng lặp vì đã tìm được phần tử
                break
        except Exception:
            # Nếu selector này không hoạt động, tiếp tục sang selector tiếp theo
            continue

    #  KHỞI TẠO DANH SÁCH DỮ LIỆU 
    # Khởi tạo danh sách rỗng để lưu trữ dữ liệu sản phẩm được trích xuất
    data = []
    # Kiểm tra xem có tìm thấy sản phẩm không
    if not products:
        # Nếu không tìm thấy, ghi log cảnh báo
        logging.warning("Không tìm thấy phần tử sản phẩm trên trang Lazada")
        # Đóng trình duyệt
        driver.quit()
        # Trả về danh sách rỗng
        return []

    #  LẶP QUA TỪNG SẢN PHẨM VÀ TRÍCH XUẤT THÔNG TIN 
    # Lặp qua tối đa 10 sản phẩm đầu tiên (products[:10])
    for idx, product in enumerate(products[:10]):
        # Khối try-except để bắt lỗi khi trích xuất dữ liệu từ sản phẩm này
        try:
            # Khởi tạo các biến để lưu trữ thông tin sản phẩm
            # Tên của sản phẩm
            title = ''
            # Giá của sản phẩm
            price = ''
            # URL hình ảnh sản phẩm
            img = ''
            # Link đến chi tiết sản phẩm
            link = ''

            #  TRÍCH XUẤT TÊN SẢN PHẨM 
            # Khối try-except để lấy tên sản phẩm
            try:
                # Tìm phần tử có CSS class .RfADt và lấy text của nó
                title = product.find_element(By.CSS_SELECTOR, ".RfADt").text
            except Exception:
                # Nếu selector trên không hoạt động, thử tìm phần tử <h3>
                try:
                    title = product.find_element(By.TAG_NAME, 'h3').text
                except Exception:
                    # Nếu cả hai không hoạt động, bỏ qua (title vẫn là '')
                    pass

            #  TRÍCH XUẤT GIÁ SẢN PHẨM 
            # Khối try-except để lấy giá (thử nhiều cách vì web hay thay đổi)
            try:
                # Tìm phần tử có CSS class .oo0xS
                price = product.find_element(By.CSS_SELECTOR, ".oo0xS").text
            except Exception:
                #  Nếu cách 1 không hoạt động, tìm span chứa ký tự ₫
                try:
                    price = product.find_element(By.XPATH, ".//span[contains(text(), '₫')]").text
                except Exception:
                    #  Tìm phần tử có attribute data-price
                    try:
                        price = product.find_element(By.CSS_SELECTOR, '[data-price]').get_attribute('data-price')
                    except Exception:
                        # : Tìm span có class chứa "price" hoặc "Price"
                        try:
                            price_elem = product.find_element(By.XPATH, ".//span[contains(@class, 'price') or contains(@class, 'Price')]")
                            price = price_elem.text
                        except Exception:
                            # Nếu tất cả không hoạt động, bỏ qua (price vẫn là '')
                            pass

            #  TRÍCH XUẤT HÌNH ẢNH SẢN PHẨM 
            # Khối try-except để lấy URL hình ảnh
            try:
                # Tìm phần tử <img> và lấy attribute src
                img = product.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
            except Exception:
                # Nếu src không tồn tại, thử lấy attribute data-src
                try:
                    img = product.find_element(By.CSS_SELECTOR, 'img').get_attribute('data-src')
                except Exception:
                    # Nếu cả hai không hoạt động, gán chuỗi rỗng
                    img = ''

            #  TRÍCH XUẤT LINK SẢN PHẨM 
            # Khối try-except để lấy link sản phẩm
            try:
                # Tìm phần tử <a> đầu tiên và lấy attribute href (link)
                link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
            except Exception:
                # Nếu không tìm được, gán chuỗi rỗng
                link = ''

            #  KIỂM TRA XEM CÓ DỮ LIỆU HỢPỆ KHÔNG
            # Nếu không có tên, hình ảnh, và link (dữ liệu trống)
            if not title and not img and not link:
                # Bỏ qua sản phẩm này và tiếp tục sang sản phẩm tiếp theo
                continue

            # THÊM DỮ LIỆU VÀO DANH SÁCH 
            # Thêm một dictionary chứa thông tin sản phẩm vào danh sách data
            data.append({
                # Tên sản phẩm (hoặc 'Không có tiêu đề' nếu không tìm được)
                'title': title or 'Không có tiêu đề',
                # Giá sản phẩm (hoặc 'N/A' nếu không tìm được)
                'price': price or 'N/A',
                # Ảnh sản phẩm (hoặc placeholder nếu không tìm được)
                'img': img or 'https://via.placeholder.com/200',
                # Link sản phẩm (hoặc '#' nếu không tìm được)
                'link': link or '#'
            })
        except Exception as e:
            # Nếu có lỗi khi xử lý sản phẩm này, bỏ qua và tiếp tục sang sản phẩm tiếp theo
            continue

    # ĐÓNG TRÌNH DUYỆT VÀ TRẢ VỀ DỮ LIỆU 
    # Đóng trình duyệt và giải phóng tài nguyên
    driver.quit()
    # Ghi log số lượng sản phẩm đã thu thập thành công
    logging.info(f"Thu thập xong: {len(data)} sản phẩm")
    # Trả về danh sách dữ liệu sản phẩm
    return data


#  5: ĐỊNH NGHĨA ROUTE TRANG CHỦ 
# Tạo route cho URL "/" (trang chủ) của ứng dụng
@app.route("/")
def home():
    # Hàm này xử lý yêu cầu HTTP khi người dùng truy cập trang chủ
    # Khối try-except để bắt lỗi khi lấy dữ liệu
    try:
        # Ghi log bắt đầu lấy dữ liệu
        logging.info("=== Bắt đầu lấy dữ liệu ===")
        # Gọi hàm get_tiki_data() để lấy dữ liệu sản phẩm từ Tiki
        products = get_tiki_data()
    except Exception as e:
        # Nếu có lỗi khi gọi get_tiki_data, ghi log lỗi đầy đủ
        logging.exception("Lỗi khi gọi get_tiki_data")
        # Trả về trang HTML với thông báo lỗi cho người dùng
        return f"<h1>Lỗi: {str(e)}</h1><p>Vui lòng kiểm tra kết nối internet hoặc thử lại sau.</p>"

    #  KIỂM TRA VÀ CHUẨN BỊ DỮ LIỆU 
    # Khởi tạo biến notice (thông báo) là None (không có thông báo)
    notice = None
    # Kiểm tra xem có sản phẩm không
    if not products:
        # Nếu không có sản phẩm thực từ Lazada, tạo thông báo cho người dùng
        notice = 'Không tìm thấy sản phẩm thực từ Lazada '
        products = [
            {},  
            {},  
            {}   
        ]

    #  RENDER TEMPLATE VÀ TRẢ VỀ 
    # Render template index.html với dữ liệu products và notice
    # Truyền products (danh sách sản phẩm) vào template
    # Truyền notice (thông báo nếu có lỗi) vào template
    return render_template("index.html", products=products, notice=notice)


# 6 ĐIỂM NHẬP VÀO CHƯƠNG TRÌNH 
# Kiểm tra xem file này có phải được chạy trực tiếp không (không phải import)
if __name__ == "__main__":
    # Ghi log thông báo Flask server đang khởi động
    logging.info("Khởi động Flask server...")
    # Chạy ứng dụng Flask với chế độ debug=True (tự khởi động lại khi có thay đổi)
    app.run(debug=True)