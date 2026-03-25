# ==========================================================
# Huong dan thuc hanh: web hien thi san pham lazada tu mysql
# file: app.py
# muc tieu: xay dung web server bang flask de doc du lieu db va hien thi
# ==========================================================

# flask:framework giup tao web server bang Python
from flask import Flask, render_template

# ham get_connection() de ket noi MySQL (da viet trong db.py)
from db import get_connection

#================================
# 1) khoi tao ung dung web flask
#================================
# Flask (__name__) giup Flask biet vi tri file dang chay de quan ly template, static...
app = Flask(__name__)

#================================
# 2) Ham lay du lieu tu MySQL
#================================
def get_products_from_db():
    # mo ket noi den MySQL thong qua ham get_connection()
    conn = get_connection()

    # tao cursor de thuc hien cau lenh SQL
    cursor = conn.cursor()

    # select de lay toan bo du lieu trong bang shop
    cursor.execute("SELECT * FROM shop")

    #fetchall() se tra ve danh sach tat ca cac san pham
    rows = cursor.fetchall()

    # dong ket noi db de tranh loi "too many connections"
    conn.close()

    # tra du lieu ve cho Flask su dung o phan giao dien
    return rows

#================================
# 3) Tao route cho website
#================================
# @app.route("/") ngia la:
# khi nguoi dung truy cap http://localhost:5000/
# -> chay ham home()
@app.route("/")
def home():

    # goi ham doc du lieu mysql
    products = get_products_from_db()

    # tra ve file html index.html trong thu muc templates/
    # dong thoi gui danh sach san pham vao bien "products" de html hien thi
    return render_template("index.html", products=products)

#================================
# 4) chay web server flask
#================================
if __name__ == "__main__":
    app.run(debug=True)
    