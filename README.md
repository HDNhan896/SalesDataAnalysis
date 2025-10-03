# 📊 Hệ Thống Phân Tích Bán Hàng

## 🚀 Giới thiệu
Đây là một **project Python** được xây dựng bởi sinh viên năm 2 trong **4 ngày làm việc (trải dài 2 tuần)**.  
Hệ thống cho phép **quản lý và phân tích dữ liệu bán hàng** từ file CSV, xuất báo cáo PDF, và trực quan hóa bằng biểu đồ/dashboard.  

👉 **Timeline phát triển:**
- **Ngày 1–3:** Xây dựng core system (import CSV, phân tích dữ liệu, phân tích sản phẩm & khách hàng).  
- **Nghỉ 1 tuần** do bận công việc.  
- **Ngày 4:** Hoàn thiện Visualization (biểu đồ, dashboard) và thêm module ML cơ bản (dự báo).  

---

## ⚙️ Chức năng chính
- **Import & kiểm tra dữ liệu**  
  - Đọc file CSV.  
  - Thống kê tổng quan: số giao dịch, sản phẩm, khách hàng, doanh thu.  

- **Phân tích theo thời gian**  
  - Doanh thu theo **tháng, quý, tuần**.  
  - So sánh tăng trưởng theo chu kỳ.  

- **Phân tích sản phẩm**  
  - Top sản phẩm bán chạy.  
  - Danh sách sản phẩm ế ẩm.  
  - Doanh thu theo danh mục.  

- **Phân tích khách hàng**  
  - Phân loại khách hàng **VIP / Thường / Vãng lai** dựa trên config JSON.  
  - Thống kê chi tiêu, tần suất mua hàng.  

- **Visualization & Báo cáo**  
  - Biểu đồ doanh thu, sản phẩm, danh mục.  
  - Dashboard tổng quan.  
  - Xuất báo cáo PDF với font Unicode (tiếng Việt không lỗi).  

- **Machine Learning (cơ bản, placeholder)**  
  - Module mở rộng cho dự báo doanh thu trong tương lai.  

---

## 🛠️ Công nghệ sử dụng
- Python 3.x  
- **CSV, JSON** để quản lý dữ liệu  
- **Matplotlib** (vẽ biểu đồ)  
- **ReportLab** (xuất báo cáo PDF)  
- Thuật toán xử lý dữ liệu thuần Python (dict, sorting, grouping)  

---

## 📂 Cấu trúc thư mục
├── sales_data.csv # Dữ liệu bán hàng
├── config.json # File cấu hình (thời gian, ngưỡng VIP, Normal)
├── SalesDataAnalysis.py # File code chính
├── sales_analysis_report_2024.pdf # Báo cáo PDF xuất ra
├── README.md # Tài liệu mô tả dự án
└── fonts/ # Font DejaVuSans cho PDF
