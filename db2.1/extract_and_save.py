# lấy dữ liệu lazada: lưu SQL

# Thư viện selenium dùng để điều khiển trình duyệt chrome tự động 
from selenium import webdriver
from selenium.webdriver.common.by import By # dùng để chọn phần tử html
from selenium.webdriver.chrome.service import Service # dùng để quản lý trình điều khiển chrome
from webdriver_manager.chrome import ChromeDriverManager # tự động tải trình điều khiển chrome
import time # dùng để tạm dừng chương trình

#import ham ket noi MySQL tu file db.py
from db import get_connection

#===============================
#Ham 1: Lay du lieu tu lazada bang selenium 
#===============================

def get_lazada_data(keyword="dien thoai"):
    # tao cau hinh trinh duyet chrome
    # headless=new de chrome chay an, khong hien cua so
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")

    # khoi tao trinh duyet chrome
    #chromeDriverManager tu dong tai dung phien ban chromedriver phu hop
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
# mo url tim kiem lazada theo tu khoa
    url = f"https://www.lazada.vn/catalog/?q={keyword}"
    driver.get(url)

    # cho 3s de web load hoan toan
    time.sleep(3)

    # tim tat ca cac san pham tren trang
    # moi san pham nam trong the <div class="Bm3ON">
    products  = driver.find_elements(By.CSS_SELECTOR, ".Bm3ON")

    # Danh sach de chua du lieu lay duoc
    data = []

    # Lay 10 san pham dau tien
    for p in products[:10]:
        try:
            # lay ten san pham (nam trong class .RfADt)
            title = p.find_element(By.CSS_SELECTOR, ".RfADt").text
            # lay gia san pham (class .oo0xS)
            price = p.find_element(By.CSS_SELECTOR, ".oo0xS").text

            # lay so luong da ban (khong phai san pham nao cung co)
            try:
                sold = p.find_element(By.CSS_SELECTOR, ".gAeZC").text
            except Exception:
                sold = "khong ro"

            # lay danh gia san pham
            try:
                rating = p.find_element(By.CSS_SELECTOR, ".Lh7ru").text
            except Exception:
                rating = "chua co"

            # Lay hinh anh san pham tu the <img>
            img = p.find_element(By.TAG_NAME, "img").get_attribute("src")

            # lay link san pham tu the <a>
            link = p.find_element(By.TAG_NAME, "a").get_attribute("href")

            # them 1 tuple du lieu vao danh sach data
            data.append((title, price, sold, rating, img, link))
        except Exception:
            # neu san pham bi loi hoac thieu du lieu -> bo qua
            continue

            # dong trinh duyet de giai phong tai nguyen 
    driver.quit()

    # tra ve danh sach du lieu lay duoc
    return data

#===============================
#Ham 2: Luu du lieu vao MySQL
#===============================

def save_to_mysql(data):
    # mo ket noi MySQL qua ham get_connection()
    conn = get_connection()
    cursor = conn.cursor()

    # Cau SQL INSERT du lieu vao bang shop
    sql = """
        INSERT INTO shop (title, price, sold, rating, img, link)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    # executemany -> chen nhieu dong du lieu cung luc 
    cursor.executemany(sql, data)

    # luu thay doi vao database
    conn.commit()

    # doing ket noi db
    conn.close()

    print("Da luu du lieu vao MySQL thanh cong!")

    #===============================
    # Phan main chay chuong trinh
    #===============================
if __name__ == "__main__":
    # 1. Goi ham lay du lieu tu lazada bang selenium
    data = get_lazada_data()

    # 2. Goi ham de luu du lieu vao MySQL
    save_to_mysql(data)

    # ket qua
    # - s3lenium mo lazada -> lay 10 san pham dau tien -> tra ve list data
    #- MySQL luu data vao bang lazada_products

    

