import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import title
import matplotlib.gridspec as gridspec
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

def output_report(data):
    # Đăng ký font DejaVu Sans
    monthly_data = get_monthly_stats(data)

    # Tính xem tháng có doanh thu nhiều nhất và thấp nhất là tháng nào
    max_month_index = max(monthly_data, key=lambda m: monthly_data[m]['revenue'])
    min_month_index = min(monthly_data, key=lambda m: monthly_data[m]['revenue'])

    day_sell = best_selling(data, 'date')  # Tính doanh thu của từng ngày
    type_sell = best_selling(data, 'category')  # Tính doanh thu của từng loại mặt hàng

    total = sum(int(row['total_amount']) for row in data[1:])  # Tính tổng doanh thu của cả file sales_data.csv
    total_Aver = total / (len(data) - 1)  # Tính tổng doang thu trung bình của cả file sales_data.csv
    best_type_top4 = list(sorted(type_sell.items(), key=lambda x: x[1],
                                 reverse=True))  # Hàm để thực hiện việc sắp xếp doanh thu của từng loại mặt hàng (lớn -> bé)

    totalFormatted = f"{total:,} VND"
    averageTotalFormatted = f"{total_Aver:,.2f} VND"
    maxMonthFormatted = f"{monthly_data[max_month_index]['revenue']:,} VND"
    minMonthFormatted = f"{monthly_data[min_month_index]['revenue']:,} VND"

    pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))  # Đảm bảo file DejaVuSans.ttf có trong thư mục fonts
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/DejaVuSans-Bold.ttf'))  # Đảm bảo file DejaVuSans.ttf có trong thư mục fonts
    # Tạo một đối tượng canvas (pdf)
    pdf_file = "output/sales_analysis_report_2024.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)

    # Sử dụng font đã đăng ký
    c.setFont("DejaVuSans", 12)  # Chọn font DejaVuSans với kích thước 1

    # Tiêu đề
    c.setFont("DejaVuSans-Bold", 16)
    c.drawString(60, 750, "========== THỐNG KÊ TỔNG QUAN ==========")

    # Thời gian phân tích
    c.setFont("DejaVuSans", 12)
    c.drawString(60, 730,
                 "Thời gian phân tích: {} đến {}".format(config["date_range"]["start"], config["date_range"]["end"]))

    # Dữ liệu cơ bản
    c.setFont("DejaVuSans-Bold", 14)
    c.drawString(60, 710, "1. Dữ liệu cơ bản:")
    c.setFont("DejaVuSans", 12)
    c.drawString(60, 690, "- Tổng số giao dịch: {}".format(len(data) - 1))
    c.drawString(60, 670, "- Tổng doanh thu: {}".format(totalFormatted))
    c.drawString(60, 650, "- Trung bình/giao dịch: {}".format(averageTotalFormatted))
    c.drawString(60, 630, "- Số sản phẩm khác nhau: {}".format(len(set(row['product_id'] for row in data[1:]))))
    c.drawString(60, 610, "- Số khách hàng: {}".format(len(set(row['customer_id'] for row in data[1:]))))

    # Theo thời gian
    c.setFont("DejaVuSans-Bold", 14)
    c.drawString(60, 570, "2. Theo thời gian:")
    c.setFont("DejaVuSans", 12)
    c.drawString(60, 550, "- Tháng cao nhất: Tháng {} ({})".format(max_month_index, maxMonthFormatted))
    c.drawString(60, 530, "- Tháng thấp nhất: Tháng {} ({})".format(min_month_index, minMonthFormatted))
    c.drawString(60, 510, "- Ngày bán nhiều nhất: {}".format(max(day_sell, key=day_sell.get)))

    # Top danh mục
    c.setFont("DejaVuSans-Bold", 14)
    c.drawString(60, 470, "3. Top danh mục:")
    c.setFont("DejaVuSans", 12)
    key, value = best_type_top4[0]
    c.drawString(60, 450, "1. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
    key, value = best_type_top4[1]
    c.drawString(60, 430, "2. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
    key, value = best_type_top4[2]
    c.drawString(60, 410, "3. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
    key, value = best_type_top4[3]
    c.drawString(60, 390, "4. {}: {} ({:.2f}%)".format(key, value, (value / total) * 100))
    c.save()
    
    print("File đã được lưu vào thư mục output.")

# Function choice
def selectOneOne():
    # Import file CSV vào
    with open('sales_data.csv', newline='', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=',')
        data = []
        start = datetime.strptime(config['date_range']['start'], "%Y-%m-%d")
        end = datetime.strptime(config['date_range']['end'], "%Y-%m-%d")
        for row in reader:
            time = datetime.strptime(row['date'], "%Y-%m-%d")
            if start <= time <= end:
                data.append(row)
                
    print("File CSV đã được nhập thành công.")
    print("Số dòng sau khi lọc:", len(data))
    print()
    return list(data)

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
  
def selectSix():
    output_report(data)
    
# Element to store data
data = []

# Main
while True:
    print()
    print("========== HỆ THỐNG PHÂN TÍCH BÁN HÀNG ==========")
    print("1. Import và xem dữ liệu")
    print(" 1.1. Import file CSV")
    print(" 1.2. Xem thống kê tổng quan")
    print(" 1.3. Kiểm tra chất lượng dữ liệu")
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
    elif choice == "6":
        selectSix()
        input("\nNhấn Enter để tiếp tục...")
    elif choice == "7":
        print("Thoát chương trình.")
        break
    
