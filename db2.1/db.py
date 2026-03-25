import pymysql
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password="Hieuthi22032005@",
        database="shop",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )