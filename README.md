# 📊 Sales Data Analysis System – Python Project

## 🚀 Giới thiệu
Sales Data Analysis là hệ thống phân tích dữ liệu bán hàng được xây dựng bằng Python, hỗ trợ phân tích doanh thu, khách hàng, sản phẩm, trực quan hóa và dự báo bằng Machine Learning.

---

# 🧠 Tính năng chính

## 1. Import & xử lý dữ liệu
- Đọc CSV  
- Lọc theo thời gian trong config.json  
- Chuẩn hóa dữ liệu (date, quantity, amount…)

## 2. Phân tích theo thời gian
- Theo tháng  
- Theo quý  
- Theo tuần  
- Tính tăng trưởng

## 3. Phân tích sản phẩm
- Top 10 bán chạy  
- Top 10 bán chậm  
- Doanh thu theo danh mục

## 4. Phân tích khách hàng
- VIP / Thường / Vãng lai  
- Tổng chi tiêu  
- Số lần mua  
- Tần suất mua  
- Lần mua gần nhất

## 5. Visualization & Dashboard
- Biểu đồ doanh thu theo tháng  
- Biểu đồ sản phẩm  
- Biểu đồ danh mục  
- Dashboard tổng hợp

## 6. Báo cáo PDF
- Xuất PDF có biểu đồ  
- Font tiếng Việt

## 7. Machine Learning – Dự báo
- Linear Regression  
- Polynomial Regression  
- Dự báo 12 tháng  
- Biểu đồ dự đoán

---

# ⚙️ Công nghệ sử dụng
- Python 3.x  
- Pandas  
- Matplotlib  
- ReportLab  
- Scikit-learn  

---

# 📂 Cấu trúc thư mục

```
project/
 ├── SalesDataAnalysis.py
 ├── config.json
 ├── sales_data.csv
 ├── README.md
 ├── charts/
 ├── output/
 ├── fonts/
```

---

# 📌 Cách chạy

## 1. Cài đặt thư viện
```
pip install pandas matplotlib reportlab scikit-learn
```

## 2. Chạy chương trình
```
python SalesDataAnalysis.py
```

---

# 📈 Machine Learning
Hệ thống dùng Linear Regression và Polynomial Regression để dự báo doanh thu theo chu kỳ tháng.

---

# 🧩 RFM Analysis
Phân khúc khách hàng dựa trên:
- Recency  
- Frequency  
- Monetary  

Tự động phân loại:
- Champions  
- Loyal Customers  
- At Risk  
- New Customers  
- Others  

---

# 📜 License
MIT License

---

# ✨ Tác giả
**Đại Nhân – Sinh viên IT năm 2**
