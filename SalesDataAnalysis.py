import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import title
import matplotlib.gridspec as gridspec
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import os
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("CẢNH BÁO: Cần cài 'scikit-learn' để chạy chức năng 6.")
    print("Chạy: pip install pandas scikit-learn")
# --- KẾT THÚC PHẦN THÊM ---
# Read configuration from JSON file
with open('config.json', 'r') as file:
    config = json.load(file)
    
    
def get_week_stats(data):
    week_data = {} # Dict rỗng
    
    for row in data[1:]:
        year, week , _ = datetime.strptime(row['date'], "%Y-%m-%d").isocalendar()
        index = f"{year}-W{week:02d}"
        
        revenue = int(row['total_amount']) # Cột doanh thu
        quantity = int(row['quantity'])
        
        # Nếu chưa có tháng này trong dict thì khởi tạo dict con
        if index not in week_data:
            week_data[index] = {"amount": 0, "transactions": 0, "quantity" : 0}

        # Cộng dồn vào tháng tương ứng
        week_data[index]["amount"] += revenue
        week_data[index]["transactions"] += 1
        week_data[index]["quantity"] += quantity
    return week_data
    
# Function to calculate total revenue per month
def get_monthly_stats(data):
    monthly_data = {} # Dict rỗng
    for i in range(1,13):
        monthly_data[i] = {"revenue" : 0, "transactions" : 0}
    for row in data[1:]:
        month_index = int(row['date'].split('-')[1]) # Lấy tháng từ cột date
        revenue = int(row['total_amount']) # Cột doanh thu

        # Cộng dồn vào tháng tương ứng
        monthly_data[month_index]["revenue"] += revenue
        monthly_data[month_index]["transactions"] += 1
    return monthly_data



def get_product_stats(data):
    products_stats = {} # Dict rỗng
    
    for row in data[1:]:
        # Lấy data từ trong csv gán cho từng dữ liệu
        product_id = row['product_id'] # Mã sản phẩm
        product_name = row['product_name'] # Tên sản phẩm
        product_category = row['category'] # Doanh mục
        product_quantity = int(row['quantity']) # Số lượng
        product_amount = int(row['total_amount']) # Doanh thu
        
        # Nếu chưa có sản phẩm này trong dict thì khởi tạo dict con
        if product_id not in products_stats:
            products_stats[product_id] = {'name': product_name, 'category': product_category, 'quantity': 0, 'amount': 0}
        
        # Cộng dồn vào sản phẩm tương ứng (số lượng và doanh thu)
        products_stats[product_id]['quantity'] += product_quantity
        products_stats[product_id]['amount'] += product_amount
        
    return products_stats



def get_customer_stats(data):
    customer_stats = {}
    
    for row in data[1:]:
        # Lấy data từ trong csv gán cho từng dữ liệu
        customer_id = row['customer_id'] # Mã khách hàng
        customer_quantity = int(row['quantity']) # Tổng sản phẩm khách hàng đã mua
        customer_purchased = int(row['total_amount']) # Tổng tiền khách đã mua
        customer_order_date = datetime.strptime(row['date'], "%Y-%m-%d") # Ngày mà khách mua hàng
        # Nếu chưa có sản phẩm này trong dict thì khởi tạo dict con
        if customer_id not in customer_stats:
            customer_stats[customer_id] = {
                'amount': customer_purchased, 
                'quantity': customer_quantity,
                'order_time' : 1,
                'first_purchase_date': customer_order_date, 
                'last_purchase_date' : customer_order_date
            }
        else:
            if customer_order_date < customer_stats[customer_id]['first_purchase_date']:
                customer_stats[customer_id]['first_purchase_date'] = customer_order_date
            
            if customer_order_date > customer_stats[customer_id]['last_purchase_date']:
                customer_stats[customer_id]['last_purchase_date'] = customer_order_date
            customer_stats[customer_id]['amount'] += customer_purchased
            customer_stats[customer_id]['quantity'] += customer_quantity
            customer_stats[customer_id]['order_time'] += 1
        
        
        # Cộng dồn vào sản phẩm tương ứng (số lượng và doanh thu)
    customer_stats = dict(sorted(customer_stats.items(), key = lambda x : x[1]['amount'] , reverse = True)) 
    return customer_stats

def get_category_stats(data):
    category_stats = {}
    category_customers = {}
    for row in data[1:]:
        category_name = row['category']
        category_quantity = int(row['quantity'])
        category_amount = int(row['total_amount'])
        customer_id = row['customer_id']
        if category_name not in category_stats:
            category_stats[category_name] = {'quantity': category_quantity, 'amount': category_amount}
            category_customers[category_name] = set([customer_id])
        else:
            category_stats[category_name]['quantity'] += category_quantity
            category_stats[category_name]['amount'] += category_amount
            category_customers[category_name].add(customer_id)
    for row in category_stats:
        category_stats[row]['customer_count'] = len(category_customers[row])
    return category_stats


# Function to find the best selling day
def best_selling(data, index):
    day_sales = {}
    for row in data[1:]:
        day = row[index]
        revenue = int(row['total_amount'])
        if day in day_sales:
            day_sales[day] += revenue
        else:
            day_sales[day] = revenue
    return day_sales

# def output_report(data):
#     # Đăng ký font DejaVu Sans
#     monthly_data = get_monthly_stats(data)

#     # Tính xem tháng có doanh thu nhiều nhất và thấp nhất là tháng nào
#     max_month_index = max(monthly_data, key=lambda m: monthly_data[m]['revenue'])
#     min_month_index = min(monthly_data, key=lambda m: monthly_data[m]['revenue'])

#     day_sell = best_selling(data, 'date')  # Tính doanh thu của từng ngày
#     type_sell = best_selling(data, 'category')  # Tính doanh thu của từng loại mặt hàng

#     total = sum(int(row['total_amount']) for row in data[1:])  # Tính tổng doanh thu của cả file sales_data.csv
#     total_Aver = total / (len(data) - 1)  # Tính tổng doang thu trung bình của cả file sales_data.csv
#     best_type_top4 = list(sorted(type_sell.items(), key=lambda x: x[1],
#                                  reverse=True))  # Hàm để thực hiện việc sắp xếp doanh thu của từng loại mặt hàng (lớn -> bé)

#     totalFormatted = f"{total:,} VND"
#     averageTotalFormatted = f"{total_Aver:,.2f} VND"
#     maxMonthFormatted = f"{monthly_data[max_month_index]['revenue']:,} VND"
#     minMonthFormatted = f"{monthly_data[min_month_index]['revenue']:,} VND"

#     pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))  # Đảm bảo file DejaVuSans.ttf có trong thư mục fonts
#     pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/DejaVuSans-Bold.ttf'))  # Đảm bảo file DejaVuSans.ttf có trong thư mục fonts
#     # Tạo một đối tượng canvas (pdf)
#     pdf_file = "output/sales_analysis_report_2024.pdf"
#     c = canvas.Canvas(pdf_file, pagesize=letter)

#     # Sử dụng font đã đăng ký
#     c.setFont("DejaVuSans", 12)  # Chọn font DejaVuSans với kích thước 1

#     # Tiêu đề
#     c.setFont("DejaVuSans-Bold", 16)
#     c.drawString(60, 750, "========== THỐNG KÊ TỔNG QUAN ==========")

#     # Thời gian phân tích
#     c.setFont("DejaVuSans", 12)
#     c.drawString(60, 730,
#                  "Thời gian phân tích: {} đến {}".format(config["date_range"]["start"], config["date_range"]["end"]))

#     # Dữ liệu cơ bản
#     c.setFont("DejaVuSans-Bold", 14)
#     c.drawString(60, 710, "1. Dữ liệu cơ bản:")
#     c.setFont("DejaVuSans", 12)
#     c.drawString(60, 690, "- Tổng số giao dịch: {}".format(len(data) - 1))
#     c.drawString(60, 670, "- Tổng doanh thu: {}".format(totalFormatted))
#     c.drawString(60, 650, "- Trung bình/giao dịch: {}".format(averageTotalFormatted))
#     c.drawString(60, 630, "- Số sản phẩm khác nhau: {}".format(len(set(row['product_id'] for row in data[1:]))))
#     c.drawString(60, 610, "- Số khách hàng: {}".format(len(set(row['customer_id'] for row in data[1:]))))

#     # Theo thời gian
#     c.setFont("DejaVuSans-Bold", 14)
#     c.drawString(60, 570, "2. Theo thời gian:")
#     c.setFont("DejaVuSans", 12)
#     c.drawString(60, 550, "- Tháng cao nhất: Tháng {} ({})".format(max_month_index, maxMonthFormatted))
#     c.drawString(60, 530, "- Tháng thấp nhất: Tháng {} ({})".format(min_month_index, minMonthFormatted))
#     c.drawString(60, 510, "- Ngày bán nhiều nhất: {}".format(max(day_sell, key=day_sell.get)))

#     # Top danh mục
#     c.setFont("DejaVuSans-Bold", 14)
#     c.drawString(60, 470, "3. Top danh mục:")
#     c.setFont("DejaVuSans", 12)
#     key, value = best_type_top4[0]
#     c.drawString(60, 450, "1. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
#     key, value = best_type_top4[1]
#     c.drawString(60, 430, "2. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
#     key, value = best_type_top4[2]
#     c.drawString(60, 410, "3. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
#     key, value = best_type_top4[3]
#     c.drawString(60, 390, "4. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
#     c.save()
    
#     print("File đã được lưu vào thư mục output.")



# Function choice
# def selectOneOne():
#     # Import file CSV vào
#     with open('sales_data.csv', newline='', encoding="utf-8-sig") as file:
#         reader = csv.DictReader(file, delimiter=',')
#         data = []
#         start = datetime.strptime(config['date_range']['start'], "%Y-%m-%d")
#         end = datetime.strptime(config['date_range']['end'], "%Y-%m-%d")
#         for row in reader:
#             time = datetime.strptime(row['date'], "%Y-%m-%d")
#             if start <= time <= end:
#                 data.append(row)
                
#     print("File CSV đã được nhập thành công.")
#     print("Số dòng sau khi lọc:", len(data))
#     print()
#     return list(data)

def generate_charts(data):
    print("🔄 Đang tạo biểu đồ...")

    # xác định đường dẫn tuyệt đối của thư mục đang chạy script
    base_path = os.path.dirname(os.path.abspath(__file__))
    charts_folder = os.path.join(base_path, "charts")

    os.makedirs(charts_folder, exist_ok=True)

    print("📁 Lưu biểu đồ vào:", charts_folder)

    try:
        # ======== Doanh thu theo tháng ========
        monthly = get_monthly_stats(data)
        months = list(monthly.keys())
        revenue = [monthly[m]['revenue'] for m in months]

        plt.figure(figsize=(10,4))
        plt.plot(months, revenue, marker='o')
        plt.title("Doanh thu theo tháng")
        plt.xlabel("Tháng")
        plt.ylabel("Doanh thu (VND)")
        plt.ticklabel_format(style='plain', axis='y')

        file1 = os.path.join(charts_folder, "DoanhThuTheoThang.png")
        plt.savefig(file1, bbox_inches="tight")
        plt.close()
        print(f"✅ Saved: {file1}")

        # ======== Top sản phẩm ========
        products = get_product_stats(data)
        top10 = sorted(products.items(), key=lambda x: x[1]['amount'], reverse=True)[:10]
        product_names = [p[1]['name'] for p in top10]
        revenues = [p[1]['amount'] for p in top10]

        plt.figure(figsize=(14,5))
        plt.bar(product_names, revenues)
        plt.title("Top 10 sản phẩm bán chạy")
        plt.xlabel("Sản phẩm")
        plt.ylabel("Doanh thu (VND)")
        plt.ticklabel_format(style='plain', axis='y')
        plt.xticks(rotation=25)

        file2 = os.path.join(charts_folder, "TopSanPham.png")
        plt.savefig(file2, bbox_inches="tight")
        plt.close()
        print(f"✅ Saved: {file2}")

        # ======== Tỷ lệ danh mục ========
        categories = get_category_stats(data)
        labels = list(categories.keys())
        sizes = [categories[c]['amount'] for c in labels]

        plt.figure(figsize=(6,6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title("Tỷ lệ doanh thu theo danh mục")

        file3 = os.path.join(charts_folder, "TyLeDanhMuc.png")
        plt.savefig(file3, bbox_inches="tight")
        plt.close()
        print(f"✅ Saved: {file3}")

    except Exception as e:
        print("❌ ERROR khi tạo biểu đồ:", e)

def generate_pdf_report(data):

    # Tạo biểu đồ trước khi xuất PDF
    generate_charts(data)

    base_path = os.path.dirname(os.path.abspath(__file__))
    charts_folder = os.path.join(base_path, "charts")
    os.makedirs(charts_folder, exist_ok=True)
    pdf_file = os.path.join(charts_folder, "BaoCao_PhanTichBanHang.pdf")
    # Đăng ký font
    pdfmetrics.registerFont(TTFont("DejaVu", "fonts/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", "fonts/DejaVuSans-Bold.ttf"))

    c = canvas.Canvas(pdf_file, pagesize=A4)
    c.setFont("DejaVu-Bold", 18)
    c.drawString(60, 800, "BÁO CÁO PHÂN TÍCH BÁN HÀNG")
    c.setFont("DejaVu", 12)
    c.drawString(60, 780, f"Tổng số dòng dữ liệu: {len(data)-1}")

    # =================== CHÈN HÌNH BIỂU ĐỒ ===================

    c.drawString(60, 750, "1. Doanh thu theo tháng:")
    c.drawImage("charts/DoanhThuTheoThang.png", 60, 470, width=480, height=250)

    c.drawString(60, 450, "2. Top sản phẩm bán chạy:")
    c.drawImage("charts/TopSanPham.png", 60, 200, width=480, height=230)

    c.showPage()  # sang trang mới

    c.drawString(60, 800, "3. Doanh thu:")
    c.drawImage("charts/TyLeDanhMuc.png", 60, 350, width=400, height=400)

    c.save()
    print(f"✅ Xuất PDF thành công -> {pdf_file}")
# === THAY THẾ HÀM selectOneOne CŨ BẰNG HÀM NÀY ===
def selectOneOne():
    """
    Nạp dữ liệu từ CSV bằng Pandas.
    1. Lưu DataFrame vào analyzer.data (cho chức năng 6).
    2. Trả về list[dict] cho các chức năng 1-5.
    """
    global data # Sử dụng biến data global
    try:
        print("Đang đọc file sales_data.csv...")
        # Dùng pandas để đọc, vì chức năng 6 BẮT BUỘC dùng pandas
        df = pd.read_csv('sales_data.csv', encoding="utf-8-sig")

        # --- Xử lý cho cả hai hệ thống ---
        # 1. Chuyển đổi cột date sang datetime (cần cho cả lọc và ML)
        df['date'] = pd.to_datetime(df['date'])
        
        # 2. Lọc theo config
        start = datetime.strptime(config['date_range']['start'], "%Y-%m-%d")
        end = datetime.strptime(config['date_range']['end'], "%Y-%m-%d")
        
        df_filtered = df[(df['date'] >= start) & (df['date'] <= end)].copy()
        
        # Chuyển đổi các cột số mà ML functions mong đợi
        df_filtered['total_amount'] = pd.to_numeric(df_filtered['total_amount'], errors='coerce').fillna(0)
        df_filtered['quantity'] = pd.to_numeric(df_filtered['quantity'], errors='coerce').fillna(0)
        df_filtered['unit_price'] = pd.to_numeric(df_filtered['unit_price'], errors='coerce').fillna(0)
        
        # Thêm các cột ngày tháng mà ML functions cần
        df_filtered['month'] = df_filtered['date'].dt.month
        df_filtered['year'] = df_filtered['date'].dt.year
        df_filtered['customer_id'] = df_filtered['customer_id'].astype(str) # Đảm bảo customer_id là string
        df_filtered['product_id'] = df_filtered['product_id'].astype(str) # Đảm bảo product_id là string

        # Nạp DataFrame đã xử lý vào analyzer
        analyzer.data = df_filtered.copy() # Lưu bản copy vào analyzer
        print("-> Đã nạp DataFrame vào 'analyzer.data' cho chức năng 6.")

        # Chuyển DataFrame về list[dict] để các hàm cũ hoạt động
        # Phải convert 'date' về string theo định dạng cũ
        df_for_list = df_filtered.copy()
        df_for_list['date'] = df_for_list['date'].dt.strftime('%Y-%m-%d')
        # Chuyển đổi lại kiểu số về string
        df_for_list['total_amount'] = df_for_list['total_amount'].astype(int).astype(str)
        df_for_list['quantity'] = df_for_list['quantity'].astype(int).astype(str)
        
        data_list_of_dicts = df_for_list.to_dict('records')
        
        print("File CSV đã được nhập thành công.")
        print("Số dòng sau khi lọc:", len(data_list_of_dicts))
        print()
        
        # Trả về list[dict] cho biến global 'data'
        return data_list_of_dicts

    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'sales_data.csv'")
        analyzer.data = None
        return []
    except Exception as e:
        print(f"Lỗi khi đọc hoặc xử lý file: {e}")
        analyzer.data = None
        return []

def selectOneTwo():
    # Khai báo 1 dictionary để tính tổng doang thu và số lượng sản phẩm đã bán của từng tháng
    monthly_data = get_monthly_stats(data) 
    
    # Tính xem tháng có doanh thu nhiều nhất và thấp nhất là tháng nào
    max_month_index = max(monthly_data, key=lambda m: monthly_data[m]['revenue'])
    min_month_index = min(monthly_data, key=lambda m: monthly_data[m]['revenue'])
    
    day_sell = best_selling(data, 'date') #Tính doanh thu của từng ngày
    type_sell = best_selling(data, 'category') #Tính doanh thu của từng loại mặt hàng
    
    total = sum(int(row['total_amount']) for row in data[1:]) #Tính tổng doanh thu của cả file sales_data.csv
    total_Aver = total / (len(data)-1) #Tính tổng doang thu trung bình của cả file sales_data.csv
    best_type_top4 = sorted(type_sell.items(), key=lambda x: x[1], reverse=True)[:4] #Hàm để thực hiện việc sắp xếp doanh thu của từng loại mặt hàng (lớn -> bé)

    #Hàm để formatted giá trị INT thành giá trị tiền tệ (1000000 -> 1,000,000 VND)
    totalFormatted = f"{total:,} VND" 
    averageTotalFormatted = f"{total_Aver:,.2f} VND"
    maxMonthFormatted = f"{monthly_data[max_month_index]['revenue']:,} VND"
    minMonthFormatted = f"{monthly_data[min_month_index]['revenue']:,} VND"
    
    
    print("\n========== THỐNG KÊ TỔNG QUAN ==========")
    print("Thời gian phân tích: {} đến {}".format(config["date_range"]["start"], config["date_range"]["end"]))
    print("\n📊 Dữ liệu cơ bản: ")
    print("- Tổng số giao dịch:", len(data)-1)
    print("- Tổng doanh thu:", totalFormatted)
    print("- Trung bình/giao dịch:", averageTotalFormatted)
    print("- Số sản phẩm khác nhau:", len(set(row['product_id'] for row in data[1:])))
    print("- Số khách hàng:", len(set(row['customer_id'] for row in data[1:])))
    print("\n📈 Theo thời gian:")
    print("- Tháng cao nhất: Tháng {} ({})".format(max_month_index, maxMonthFormatted))
    print("- Tháng thấp nhất: Tháng {} ({})".format(min_month_index, minMonthFormatted))
    print("- Ngày bán nhiều nhất:", max(day_sell, key=day_sell.get))
    print()
    print("🏆 Top danh mục:")
    for i in range(1,5):
        print("{}. {}: {} ({:.2f}%)".format(i, best_type_top4[i - 1][0], f"{best_type_top4[i - 1][1]:,} VND", (best_type_top4[i - 1][1] / total) * 100))
        
    
def selectTwoOne():
    monthly_data = get_monthly_stats(data)
    
    print("\n===================== DOANH THU THEO THÁNG NĂM 2024 ======================")
    print("| Tháng | Doanh thu (VND)    | Số GD | TB/GD (VND) | So với tháng trước  |")
    print("|-------|--------------------|-------|-------------|---------------------| ")
    for i in range (1,13):
        revenue = monthly_data[i]['revenue']
        transactions = monthly_data[i]['transactions']
        avg = revenue / transactions if transactions else 0

        if i == 1:
            change_str = "..."
        else:
            prev = monthly_data[i - 1]['revenue']
            change = ((revenue / prev) * 100) - 100 if prev else 0 # Chỉ thực hiện khi prev != 0
            change_str = f"↓{change:,.2f}%" if change < 0 else f"↑+{change:,.2f}%"   # Định dạng có dấu %

        print(f"| {i:<6}| {revenue:<19,}| {transactions:<6}| {avg:<12.2f}| {change_str:<19} |")
    print("==========================================================================")
    
def selectTwoTwo():
    monthly_data = get_monthly_stats(data)
    index = 1
    total_3_month = 0
    total_3_transactions = 0
    prev_total_3_month = None 
    
    print("\n====================== DOANH THU THEO QUÝ NĂM 2024 ====================")
    print("| Tháng | Doanh thu (VND)    | Số GD | TB/GD (VND) | So với quý trước |")
    print("|-------|--------------------|-------|-------------|------------------|")
    for i in range (1,13):
        revenue = monthly_data[i]['revenue']
        transactions = monthly_data[i]['transactions']
        total_3_transactions += transactions
        total_3_month += revenue
        avg = total_3_month / total_3_transactions if total_3_transactions else 0
        
        if i % 3 == 0:
            if i == 3:
                change_str = "..."
            else:
                change = ((total_3_month / prev_total_3_month) * 100) - 100 if prev_total_3_month else 0 # Chỉ thực hiện khi prev != 0
                change_str = f"↓{change:,.2f}%" if change < 0 else f"↑+{change:,.2f}%"   # Định dạng có dấu %
                
            print(f"| Quý {(index):<2}| {total_3_month:<19,}| {total_3_transactions:<6}| {avg:<12.2f}| {change_str:<17}|")
            index += 1
            prev_total_3_month = total_3_month
            total_3_month = 0
            total_3_transactions = 0
    print("=======================================================================")

def selectTwoThree():
    week_data = get_week_stats(data)
    week_data = dict(sorted(week_data.items(), key = lambda x : x[0] , reverse = False))
    prev_week = None 
    
    print("\n==================== DOANH THU THEO TUẦN NĂM 2024 ====================")
    print("| Tuần | Doanh thu (VND)    | Số GD | TB/GD (VND) | So với tuần trước |")
    print("|------|--------------------|-------|-------------|-------------------|")
    for row in week_data:
        week = int(row[6:])
        week_amount = week_data[row]['amount']
        week_transactions = week_data[row]['transactions']
        week_amount_average = week_amount/week_transactions
        if week == 1:
            change_str = "..."
        else:
            change = ((week_amount / week_data[prev_week]['amount']) * 100) - 100 if prev_week else 0 # Chỉ thực hiện khi prev != 0
            change_str = f"↓{change:,.2f}%" if change < 0 else f"↑+{change:,.2f}%"   # Định dạng có dấu %
        prev_week = row
        week_amount = f"{week_amount:,} VND"
        print(f"| {week:<4} | {week_amount:>18} | {week_transactions:>5} | {week_amount_average:>11.2f} | {change_str:<17} |")
        
    print("=======================================================================")


def selectThreeOne():
    products_data = get_product_stats(data)
    products_data_top10 = dict(sorted(products_data.items(), key = lambda x : x[1]['amount'], reverse = True)[:10])
    index = 0
    total = sum(int(row['total_amount']) for row in data[1:])
    print("\n================================== TOP 10 SẢN PHẨM BÁN CHẠY =================================")
    print("| Hạng | Mã SP | Tên sản phẩm              | Danh mục    | Số lượng | Doanh thu     | Tỷ lệ |")
    print("|------|-------|---------------------------|-------------|----------|---------------|-------|")
    for product in products_data_top10:
        product_id = product # Mã sản phẩm
        product_name = products_data_top10[product]['name'] # Tên sản phẩm
        product_category = products_data_top10[product]['category'] # Doanh mục
        product_quantity = products_data_top10[product]['quantity'] # Số lượng
        product_amount = f"{products_data_top10[product]['amount']:,} VND" # Doanh thu
        change = f"{((float(products_data_top10[product]['amount'] * 100)) / total) :,.2f}%"
        print(f"| {index + 1:<4} | {product_id:<6}| {product_name:<26}| {product_category:<12}| {product_quantity:<9}| {product_amount:<14}| {change:<6}|")
        index += 1
    print("=============================================================================================")
    
def selectThreeTwo():
    total = sum(int(row['total_amount']) for row in data[1:])
    type_sell = get_category_stats(data)       
    type_sell = dict(sorted(type_sell.items(), key = lambda x : x[1]['amount'], reverse = True)) 
    print("\n===================== PHÂN TÍCH THEO DOANH MỤC =======================")
    print("|    Danh mục    | Doanh thu (VND) | Số lượng | Khách hàng |  Tỷ lệ  |")
    print("|----------------|-----------------|----------|------------|---------|") 
    for row in type_sell:
        category_name = row
        category_amount = f"{type_sell[row]['amount']:,} VND"
        category_quantity = type_sell[row]['quantity']
        customer_count = type_sell[row]['customer_count']
        revenue_percent = f"{(type_sell[row]['amount'] / total) * 100:,.2f}%"
        
        print(f"| {category_name:15}| {category_amount:>14} | {category_quantity:> 8} | {customer_count:>10} | {revenue_percent:<7} |")
    print("======================================================================")  
    
def selectThreeThree():
    products_data = get_product_stats(data)
    products_data_worst = dict(sorted(products_data.items(), key = lambda x : x[1]['amount'], reverse = False)[:10])
    index = 0
    total = sum(int(row['total_amount']) for row in data[1:])
    print("\n=================================== TOP 10 SẢN PHẨM BÁN Ế ===================================")
    print("| Hạng | Mã SP | Tên sản phẩm              | Danh mục    | Số lượng | Doanh thu     | Tỷ lệ |")
    print("|------|-------|---------------------------|-------------|----------|---------------|-------|")
    for product in products_data_worst:
        product_id = product # Mã sản phẩm
        product_name = products_data_worst[product]['name'] # Tên sản phẩm
        product_category = products_data_worst[product]['category'] # Doanh mục
        product_quantity = products_data_worst[product]['quantity'] # Số lượng
        product_amount = f"{products_data_worst[product]['amount']:,} VND" # Doanh thu
        change = f"{((float(products_data_worst[product]['amount'] * 100)) / total) :,.2f}%"
        print(f"| {index + 1:<4} | {product_id:<6}| {product_name:<26}| {product_category:<12}| {product_quantity:<9}| {product_amount:<14}| {change:<6}|")
        index += 1
    print("=============================================================================================")   
    
def selectFourOne():
    vip_requirement = config["vip_requirement"]
    customer_data = get_customer_stats(data)
    print("\n========================= DANH SÁCH KHÁCH HÀNG VIP ========================")
    print("| Mã khách hàng |   Tổng chi tiêu   | Đã mua | Mua gần đây | Tần suất mua |")
    print("|---------------|-------------------|--------|-------------|--------------|")
    for row in customer_data:
        # Lấy dữ liệu của từng khách hàng
        customer_id = row
        customer_amount = customer_data[row]['amount']
        customer_quantity = customer_data[row]['quantity']
        customer_last_order_date = customer_data[row]['last_purchase_date']
        months = ((customer_data[row]['last_purchase_date'] - customer_data[row]['first_purchase_date']).days) / 30
        
        
        if months == 0:
            purchase_frequency = customer_quantity  
        else:
            purchase_frequency = customer_quantity / months
        # Nếu khách hàng mua trên 7,500,000 VND thì sẽ là khách VIP
        if customer_amount >= vip_requirement:
            customer_amount = f"{customer_amount:,} VND"
            last_date_str = customer_last_order_date.strftime("%Y-%m-%d")
            print(f"|    {customer_id:<11}|  {customer_amount:>17}|{customer_quantity:>7} |{last_date_str:>12} | {int(purchase_frequency):>2} lần/tháng |")
    print("===========================================================================")
    
def selectFourTwo():
    selectFourOne()
    vip_requirement = config["vip_requirement"]
    normal_requirement = config["normal_requirement"]
    customer_data = get_customer_stats(data)
    
    print("\n======================== DANH SÁCH KHÁCH HÀNG THƯỜNG ======================")
    print("| Mã khách hàng |   Tổng chi tiêu   | Đã mua | Mua gần đây  | Tần suất mua |")
    print("|---------------|-------------------|--------|--------------|--------------|")
    for row in customer_data:
        # Lấy dữ liệu của từng khách hàng
        customer_id = row
        customer_amout = customer_data[row]['amount']
        customer_quantity = customer_data[row]['quantity']
        customer_last_order_date = customer_data[row]['last_purchase_date']
        months = ((customer_data[row]['last_purchase_date'] - customer_data[row]['first_purchase_date']).days) / 30
        if months == 0:
            purchase_frequency = customer_quantity  
        else:
            purchase_frequency = customer_quantity / months
            
        if customer_amout < vip_requirement and customer_amout >= normal_requirement:
            customer_amout = f"{customer_amout:,} VND"
            last_date_str = customer_last_order_date.strftime("%Y-%m-%d")
            print(f"|    {customer_id:<11}|  {customer_amout:>17}|{customer_quantity:>7} | {last_date_str:>12} | {int(purchase_frequency):>2} lần/tháng |")
    print("============================================================================")
    
    print("\n======================= DANH SÁCH KHÁCH HÀNG VÃNG LAI =====================")
    print("| Mã khách hàng |   Tổng chi tiêu   | Đã mua | Mua gần đây  | Tần suất mua |")
    print("|---------------|-------------------|--------|--------------|--------------|")
    for row in customer_data:
        customer_id = row
        customer_amout = customer_data[row]['amount']
        customer_quantity = customer_data[row]['quantity']
        customer_last_order_date = customer_data[row]['last_purchase_date']
        months = ((customer_data[row]['last_purchase_date'] - customer_data[row]['first_purchase_date']).days) / 30
        if months == 0:
            purchase_frequency = customer_quantity  
        else:
            purchase_frequency = customer_quantity / months
            
        if customer_amout < normal_requirement:
            customer_amout = f"{customer_amout:,} VND"
            last_date_str = customer_last_order_date.strftime("%Y-%m-%d")
            print(f"|    {customer_id:<11}|  {customer_amout:>17}|{customer_quantity:>7} | {last_date_str:>12} | {int(purchase_frequency):>2} lần/tháng |")
    print("============================================================================")

def selectFiveOne():
    global data  # Sử dụng biến toàn cục đã load ở bước 1.1
    if not data:
        print("Vui lòng nhập dữ liệu trước (1.1)!")
        return

    print("\n========== TẠO BIỂU ĐỒ ==========")
    print("1. Biểu đồ doanh thu theo tháng")
    print("2. Biểu đồ top sản phẩm bán chạy")
    print("3. Biểu đồ tỷ lệ doanh thu theo danh mục")
    print("4. Quay lại")

    sub_choice = input("Chọn loại biểu đồ (1-4): ")
    if sub_choice == '1':
        monthly = get_monthly_stats(data)
        months = list(monthly.keys())
        revenue = [monthly[m]['revenue']for m in months]
        plt.figure(figsize=(10,5))
        plt.plot(months, revenue, marker='o', color='blue')
        plt.title("Doanh thu theo tháng")
        plt.xlabel("Tháng")
        plt.ylabel("Doanh thu (VNĐ)")
        plt.grid(True)
        plt.show()
    elif sub_choice == "2":
        products = get_product_stats(data)
        top10 = sorted(products.items(), key=lambda x: x[1]['amount'], reverse=True)[:10]
        product_names = [p[1]['name'] for p in top10]
        revenues = [p[1]['amount'] for p in top10]
        plt.figure(figsize=(15, 6))
        plt.bar(product_names, revenues, color='green')  # Biểu đồ cột dọc
        plt.title("Top 10 sản phẩm bán chạy")
        plt.xlabel("Sản phẩm")
        plt.ylabel("Doanh thu (VND)")
        plt.xticks(rotation=0, ha='center')  # Xoay nhãn trục x để dễ đọc
        plt.tight_layout()
        plt.show()
    elif sub_choice == "3":
        categories = get_category_stats(data)
        labels = list(categories.keys())
        sizes = [categories[c]['amount'] for c in labels]
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=140)
        plt.title("Tỷ lệ doanh thu theo danh mục")
        plt.axis("equal")
        plt.show()

    elif sub_choice == "4":
        return plt
    else:
        print("Lựa chọn không hợp lệ.")
    return plt

def selectFiveTwo():
    fig = plt.figure(figsize=(20,10))
    gs = gridspec.GridSpec(2,2, height_ratios=[1,1.2])

    monthly = get_monthly_stats(data)
    months = list(monthly.keys())
    revenue = [monthly[m]['revenue'] for m in months]

    products = get_product_stats(data)
    top10 = sorted(products.items(), key=lambda x: x[1]['amount'], reverse=True)[:10]
    product_names = [p[1]['name'] for p in top10]
    revenues = [p[1]['amount'] for p in top10]

    categories = get_category_stats(data)
    labels = list(categories.keys())
    sizes = [categories[c]['amount'] for c in labels]

    axs1 = fig.add_subplot(gs[0, 0])
    axs1.plot(months, revenue, color='blue')
    axs1.set_title("Biểu đồ doanh thu theo tháng")
    axs1.set_ylabel('VND')

    axs2 = fig.add_subplot(gs[1, :])
    axs2.bar(product_names, revenues, color='green')
    axs2.set_title("Top 10 sản phẩm bán chạy")
    axs2.set_ylabel('VND')

    axs3 = fig.add_subplot(gs[0, 1])
    axs3.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=140)
    axs3.set_title("Biểu đồ tỷ lệ doanh thu theo danh mục")

    plt.tight_layout()
    fig.suptitle("DASHBOARD TỔNG QUAN", fontsize=12, y=1)
    plt.show()
  
def selectFiveThree():
    generate_pdf_report(data)

# def selectSix():
#     output_report(data)

# ... (Tất cả các hàm get_... và select... của bạn ở trên) ...

class SalesAnalyzer:
    def __init__(self):
        self.data = None # Dữ liệu DataFrame sẽ được lưu ở đây
        print("SalesAnalyzer đã sẵn sàng. Vui lòng nạp dữ liệu (1.1).")

    # === DI CHUYỂN CÁC HÀM CÓ 'self' VÀO ĐÂY ===
    
    def sales_forecasting(self, periods=12):
        """Dự đoán doanh số bán hàng"""
        if self.data is None:
            print("Lỗi: Chưa có dữ liệu (self.data is None)")
            return
        if not SKLEARN_AVAILABLE:
            print("Lỗi: Thiếu thư viện scikit-learn.")
            return

        print("\nDỰ ĐOÁN DOANH SỐ BÁN HÀNG")
        print("="*50)
        try:
            # Chuẩn bị dữ liệu theo tháng
            # Dùng 'date' (đã convert ở 1.1) và 'total_amount'
            monthly_data = self.data.groupby(self.data['date'].dt.to_period('M')).agg({
                'total_amount': 'sum'
            }).reset_index()
            monthly_data['date'] = monthly_data['date'].dt.to_timestamp()
            monthly_data['month_num'] = range(len(monthly_data))
            
            if len(monthly_data) < 5: # Cần ít nhất 1 ít dữ liệu
                print("Lỗi: Không đủ dữ liệu hàng tháng để dự đoán.")
                return

            # Tách train/test (80/20)
            train_size = int(len(monthly_data) * 0.8)
            # Đảm bảo test set có ít nhất 1 mẫu
            if train_size >= len(monthly_data):
                train_size = len(monthly_data) - 1
            
            train_data = monthly_data[:train_size]
            test_data = monthly_data[train_size:]
            
            X_train = train_data[['month_num']]
            y_train = train_data['total_amount']
            X_test = test_data[['month_num']]
            y_test = test_data['total_amount']

            # Model 1: Linear Regression
            linear_model = LinearRegression()
            linear_model.fit(X_train, y_train)
            
            # Model 2: Polynomial Regression (bậc 2)
            poly_features = PolynomialFeatures(degree=2)
            X_train_poly = poly_features.fit_transform(X_train)
            X_test_poly = poly_features.transform(X_test)
            poly_model = LinearRegression()
            poly_model.fit(X_train_poly, y_train)
            
            # Đánh giá models (chỉ khi có test data)
            if not X_test.empty:
                linear_pred = linear_model.predict(X_test)
                poly_pred = poly_model.predict(X_test_poly)
                linear_mae = mean_absolute_error(y_test, linear_pred)
                poly_mae = mean_absolute_error(y_test, poly_pred)
                linear_r2 = r2_score(y_test, linear_pred)
                poly_r2 = r2_score(y_test, poly_pred)
                
                print("Đánh giá Models:")
                print(f" - Linear Regression - MAE: {linear_mae:,.0f}, R2: {linear_r2:.3f}")
                print(f" - Polynomial (deg=2) - MAE: {poly_mae:,.0f}, R2: {poly_r2:.3f}")
                
                # Chọn model tốt hơn
                best_model = poly_model if poly_r2 > linear_r2 else linear_model
                best_model_name = "Polynomial" if poly_r2 > linear_r2 else "Linear"
                features = poly_features if poly_r2 > linear_r2 else None
            else:
                print("Không đủ dữ liệu để test, dùng Polynomial làm mặc định.")
                best_model = poly_model
                best_model_name = "Polynomial"
                features = poly_features

            print(f"\nModel được chọn: {best_model_name}")
            
            # Dự đoán tương lai
            last_month_num = monthly_data['month_num'].max()
            future_months = range(last_month_num + 1, last_month_num + 1 + periods)
            if features: # Polynomial
                future_X = features.transform([[month] for month in future_months])
            else: # Linear
                future_X = [[month] for month in future_months]
            future_predictions = best_model.predict(future_X)
            
            # Tạo dates cho predictions
            last_date = monthly_data['date'].max()
            # Sửa lại cách tạo future_dates bằng pd.DateOffset
            future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, periods + 1)]

            # Display predictions
            print(f"\nDỰ ĐOÁN {periods} THÁNG TIẾP THEO:")
            print(f"{'Tháng':<12} {'Dự đoán (VND)':<15} {'Tăng trưởng':<12}")
            print("-" * 45)
            last_actual = monthly_data['total_amount'].iloc[-1]
            
            for i, (date, pred) in enumerate(zip(future_dates, future_predictions)):
                month_str = date.strftime("%Y-%m")
                if i == 0:
                    growth = ((pred - last_actual) / last_actual) * 100
                else:
                    growth = ((pred - future_predictions[i-1]) / future_predictions[i-1]) * 100
                growth_str = f"{growth:+.1f}%"
                print(f"{month_str:<12} {pred:>14,.0f} {growth_str:>11}")
                
            # Visualization
            self.plot_forecast(monthly_data, future_dates, future_predictions, best_model_name)
            
        except Exception as e:
            print(f"Lỗi xảy ra trong khi dự đoán: {e}")

    def plot_forecast(self, historical_data, future_dates, predictions, model_name):
        plt.figure(figsize=(15, 8))
        # ... (Toàn bộ code của plot_forecast dán vào đây) ...
        plt.plot(historical_data['date'], historical_data['total_amount'], marker='o', linewidth=2, label='Dữ liệu lịch sử', color='blue')
        plt.plot(future_dates, predictions, marker='s', linewidth=2, linestyle='--', label='Dự đoán', color='red')
        plt.title(f'Dự đoán Doanh thu bằng {model_name} Regression', fontsize=16, fontweight='bold')
        plt.xlabel('Thời gian')
        plt.ylabel('Doanh thu (VND)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('output/sales_forecast.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Đã lưu biểu đồ dự đoán: sales_forecast.png")


    def customer_segmentation(self):
        """Phân khúc khách hàng bằng RFM Analysis"""
        if self.data is None:
            print("Lỗi: Chưa có dữ liệu (self.data is None)")
            return
            
        print("\nPHÂN KHÚC KHÁCH HÀNG (RFM ANALYSIS)")
        print("="*60)
            
        if 'customer_id' not in self.data.columns:
            print("X Không có thông tin customer_id trong dữ liệu")
            return None
        # ... (Toàn bộ code của customer_segmentation dán vào đây) ...
        current_date = self.data['date'].max()
        rfm = self.data.groupby('customer_id').agg({
            'date': lambda x: (current_date - x.max()).days, # Recency
            'product_id': 'count', # Frequency
            'total_amount': 'sum' # Monetary
        }).reset_index()
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
        def segment_customers(row):
            if row['rfm_score'] in ['555', '554', '544', '545', '454', '455', '445']: return 'Champions'
            elif row['rfm_score'] in ['543', '444', '435', '355', '354', '345', '344', '335']: return 'Loyal Customers'
            elif row['rfm_score'] in ['512', '511', '422', '421', '412', '411', '311']: return 'Potential Loyalists'
            elif row['rfm_score'] in ['512', '511', '331', '321', '312', '231', '241', '251']: return 'New Customers'
            elif row['rfm_score'] in ['155', '154', '144', '214', '215', '115', '114']: return 'At Risk'
            elif row['rfm_score'] in ['155', '154', '144', '214', '215', '115']: return 'Cannot Lose Them'
            else: return 'Others'
        rfm['segment'] = rfm.apply(segment_customers, axis=1)
        segment_analysis = rfm.groupby('segment').agg({'customer_id': 'count', 'recency': 'mean', 'frequency': 'mean', 'monetary': 'mean'}).round(2)
        segment_analysis.columns = ['customer_count', 'avg_recency', 'avg_frequency', 'avg_monetary']
        segment_analysis['percentage'] = (segment_analysis['customer_count'] / len(rfm) * 100).round(1)
        print(f"{'Phân khúc':<20} {'Số KH':<8} {'Tỷ lệ':<8} {'R':<6} {'F':<6} {'M (VND)':<12}")
        print("-" * 75)
        for segment, row in segment_analysis.iterrows():
            print(f"{segment:<20} {row['customer_count']:>7} {row['percentage']:>6.1f}% {row['avg_recency']:>5.0f} {row['avg_frequency']:>5.1f} {row['avg_monetary']:>11,.0f}")
        champions = segment_analysis.loc['Champions'] if 'Champions' in segment_analysis.index else None
        if champions is not None:
            print(f"\nChampions: {champions['customer_count']} khách hàng ({champions['percentage']:.1f}%)")
            print(f" - Mua trung bình {champions['avg_frequency']:.1f} lần")
            print(f" - Chi tiêu trung bình {champions['avg_monetary']:,.0f} VND/khách")
        return rfm


    def advanced_analytics(self):
        """Phân tích nâng cao và insights"""
        if self.data is None:
            print("Lỗi: Chưa có dữ liệu (self.data is None)")
            return
            
        print("\nPHÂN TÍCH NÂNG CAO")
        print("="*50)
        # ... (Toàn bộ code của advanced_analytics dán vào đây) ...
        numeric_cols = ['quantity', 'unit_price', 'total_amount']
        correlation_matrix = self.data[numeric_cols].corr()
        print("Ma trận tương quan:")
        print(correlation_matrix.round(3))
        product_lifecycle = self.data.groupby(['product_id', 'product_name']).agg({'date': ['min', 'max'], 'total_amount': 'sum', 'quantity': 'sum'}).reset_index()
        product_lifecycle.columns = ['product_id', 'product_name', 'first_sale', 'last_sale', 'total_revenue', 'total_quantity']
        product_lifecycle['product_age'] = (product_lifecycle['last_sale'] - product_lifecycle['first_sale']).dt.days
        product_lifecycle['daily_avg_revenue'] = product_lifecycle['total_revenue'] / (product_lifecycle['product_age'] + 1)
        top_daily_performers = product_lifecycle.nlargest(5, 'daily_avg_revenue')
        print(f"\nTop 5 sản phẩm hiệu suất cao nhất (doanh thu/ngày):")
        for _, row in top_daily_performers.iterrows():
            print(f" - {row['product_name'][:30]}: {row['daily_avg_revenue']:,.0f} VND/ngày")
        monthly_category = self.data.groupby(['month', 'category'])['total_amount'].sum().reset_index()
        print("\nPhân tích mùa vụ theo danh mục:")
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for category in self.data['category'].unique():
            cat_data = monthly_category[monthly_category['category'] == category]
            if not cat_data.empty:
                best_month = cat_data.loc[cat_data['total_amount'].idxmax(), 'month']
                print(f" - {category}: Tháng {best_month} ({month_names[best_month-1]}) bán chạy nhất")
        # self.create_correlation_heatmap(correlation_matrix) # Tạm thời tắt để tránh lỗi
        return {'correlation': correlation_matrix, 'product_lifecycle': product_lifecycle, 'seasonal_analysis': monthly_category}

# === KẾT THÚC CLASS ===
analyzer = SalesAnalyzer()
def selectSix():
    """Chạy chức năng 6: Dự đoán và Phân tích ML"""
    print("\n--- Bắt đầu Chức năng 6: Dự đoán và ML ---")
    
    # Kiểm tra xem dữ liệu đã được load chưa
    if analyzer.data is None:
        print("X Lỗi: Chưa import dữ liệu.")
        print("Vui lòng chạy chức năng 1.1 trước.")
        return # Dừng lại nếu không có dữ liệu

    # 1. Gọi hàm dự đoán
    analyzer.sales_forecasting()
    
    # 2. Gọi hàm phân tích nâng cao
    analyzer.advanced_analytics()
    
    print("\n--- Hoàn tất Chức năng 6 ---")
# Element to store data
data = []

# Main
while True:
    print()
    print("========== HỆ THỐNG PHÂN TÍCH BÁN HÀNG ==========")
    print("1. Import và xem dữ liệu")
    print(" 1.1. Import file CSV và kiểm tra chất lượng dữ liệu ")
    print(" 1.2. Xem thống kê tổng quan")
    print("2. Phân tích theo thời gian")
    print(" 2.1. Doanh thu theo tháng")
    print(" 2.2. Doanh thu theo quý ")
    print(" 2.3. Xu hướng theo tuần")
    print("3. Phân tích sản phẩm")
    print(" 3.1. Top sản phẩm bán chạy")
    print(" 3.2. Phân tích theo danh mục")
    print(" 3.3. Sản phẩm ế ẩm")
    print("4. Phân tích khách hàng")
    print(" 4.1. Khách hàng VIP")
    print(" 4.2. Phân khúc khách hàng")
    print("5. Visualization và báo cáo")
    print(" 5.1. Tạo biểu đồ")
    print(" 5.2. Dashboard tổng quan")
    print(" 5.3. Xuất báo cáo")
    print("6. Dự đoán và ML")
    print("7. Thoát")
    choice = input("\nChọn chức năng (1-7): ")
    
    if choice == "1.1":
        data = selectOneOne()
        input("Nhấn Enter để tiếp tục...")
    elif choice == "1.2":
        selectOneTwo()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "1.3":
        print("Kiểm tra chất lượng dữ liệu...")
    elif choice == "2.1":
        selectTwoOne()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "2.2":
        selectTwoTwo()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "2.3":
        selectTwoThree()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "3.1":
        selectThreeOne()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "3.2":
        selectThreeTwo()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "3.3":
        selectThreeThree()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "4.1":
        selectFourOne()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "4.2":
        selectFourTwo()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "5.1":
        selectFiveOne()
    elif choice == "5.2":
        selectFiveTwo()
    elif choice == "5.3":
        print("Xuất báo cáo...")
        selectFiveThree()
        input("Nhấn Enter để tiếp tục...")
    elif choice == "6":
        selectSix()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "7":
        print("Thoát chương trình.")
        break
    
