import socket
import struct
import json
import time
import threading

# ================= 配置与模拟数据 =================

HOST = '127.0.0.1'
PORT = 34206

# 1. 模拟数据库：用户表 (预置一个账号 admin/123456)
users_db = [
    {"id": 100, "username": "admin", "password": "123", "balance": 99999}
]

# 2. 模拟数据库：机场表
airports_db = [
    {"iata": "PEK", "city": "北京", "name": "首都国际机场"},
    {"iata": "PKX", "city": "北京", "name": "大兴国际机场"},
    {"iata": "SHA", "city": "上海", "name": "虹桥国际机场"},
    {"iata": "PVG", "city": "上海", "name": "浦东国际机场"},
    {"iata": "CAN", "city": "广州", "name": "白云国际机场"},
    {"iata": "SZX", "city": "深圳", "name": "宝安国际机场"}
]

# 3. 模拟数据库：航班表 (包含余票 tickets_left)
flights_db = [
    {
        "id": 501, "flight_no": "CA1501", 
        "src_iata": "PEK", "dest_iata": "SHA", 
        "dep_time": "2023-12-25 08:00", "arr_time": "2023-12-25 10:30", 
        "price": 800, "tickets_left": 5
    },
    {
        "id": 502, "flight_no": "MU5123", 
        "src_iata": "PKX", "dest_iata": "PVG", 
        "dep_time": "2023-12-25 09:00", "arr_time": "2023-12-25 11:30", 
        "price": 750, "tickets_left": 0 # 售罄测试
    },
    {
        "id": 503, "flight_no": "CZ3001", 
        "src_iata": "CAN", "dest_iata": "PEK", 
        "dep_time": "2023-12-26 14:00", "arr_time": "2023-12-26 17:00", 
        "price": 1200, "tickets_left": 20
    }
]

# 4. 模拟数据库：订单表
orders_db = []

# ================= 核心逻辑 =================

def send_packet(conn, json_data):
    """打包并发送：4字节长度头 + JSON body"""
    body = json.dumps(json_data).encode('utf-8')
    header = struct.pack('>I', len(body)) # Big-endian 4字节整数
    conn.sendall(header + body)
    print(f"   📤 [Resp] {json_data.get('type')}")

def handle_client(conn, addr):
    print(f"✅ 新连接: {addr}")
    try:
        while True:
            # 1. 读取头部 (4字节)
            header = conn.recv(4)
            if not header: break
            
            # 2. 解析长度
            body_len = struct.unpack('>I', header)[0]
            
            # 3. 读取数据体
            body = b""
            while len(body) < body_len:
                packet = conn.recv(body_len - len(body))
                if not packet: break
                body += packet
            
            if not body: break

            # 4. 处理业务逻辑
            req = json.loads(body.decode('utf-8'))
            req_type = req.get('type')
            print(f"📩 [Recv] {req_type} -> {req}")
            
            response = {}

            # --- A. 注册 ---
            if req_type == "register":
                new_user = req.get('username')
                new_pass = req.get('password')
                # 检查是否重复
                if any(u['username'] == new_user for u in users_db):
                    response = {"type": "register_res", "result": False, "message": "用户名已存在"}
                else:
                    new_id = users_db[-1]['id'] + 1
                    users_db.append({"id": new_id, "username": new_user, "password": new_pass, "balance": 0})
                    response = {"type": "register_res", "result": True, "message": "注册成功"}

            # --- B. 登录 ---
            elif req_type == "login":
                user = req.get('username')
                pwd = req.get('password')
                found = next((u for u in users_db if u['username'] == user and u['password'] == pwd), None)
                if found:
                    response = {
                        "type": "login_res", 
                        "result": True, 
                        "user_id": found['id'], 
                        "message": f"欢迎回来, {user}"
                    }
                else:
                    response = {"type": "login_res", "result": False, "message": "账号或密码错误"}

            # --- C. 获取机场列表 ---
            elif req_type == "get_airports":
                response = {"type": "get_airports_res", "data": airports_db}

            # --- D. 查询航班 (按城市) ---
            elif req_type == "search_flights":
                src_city = req.get('src_city')
                dest_city = req.get('dest_city')
                
                # 1. 找出该城市对应的所有 IATA 代码
                src_iatas = [a['iata'] for a in airports_db if a['city'] == src_city]
                dest_iatas = [a['iata'] for a in airports_db if a['city'] == dest_city]
                
                # 2. 筛选航班
                matched_flights = []
                for f in flights_db:
                    if f['src_iata'] in src_iatas and f['dest_iata'] in dest_iatas:
                        # (可选: 这里可以加日期过滤逻辑，目前简化处理返回所有)
                        matched_flights.append(f)
                
                response = {"type": "search_flights_res", "flights": matched_flights}

            # --- E. 购买机票 (扣库存) ---
            elif req_type == "buy_ticket":
                f_id = req.get('flight_id')
                u_id = req.get('user_id')
                
                target_flight = next((f for f in flights_db if f['id'] == f_id), None)
                
                if target_flight:
                    if target_flight['tickets_left'] > 0:
                        # 扣票
                        target_flight['tickets_left'] -= 1
                        # 生成订单
                        orders_db.append({
                            "order_id": len(orders_db) + 9000,
                            "user_id": u_id,
                            "flight_id": f_id,
                            "order_time": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        response = {"type": "buy_ticket_res", "result": True, "message": "购票成功"}
                    else:
                        response = {"type": "buy_ticket_res", "result": False, "message": "已售罄"}
                else:
                    response = {"type": "buy_ticket_res", "result": False, "message": "航班不存在"}

            # --- F. 我的订单 ---
            elif req_type == "my_orders":
                u_id = req.get('user_id')
                my_list = []
                
                # 联查：从 orders 表找 flight_id，再去 flights 表找详情
                for order in orders_db:
                    if order['user_id'] == u_id:
                        # 找到对应的航班信息
                        flight = next((f for f in flights_db if f['id'] == order['flight_id']), None)
                        if flight:
                            # 组合数据返回给前端
                            my_list.append({
                                "order_id": order['order_id'],
                                "flight_no": flight['flight_no'],
                                "src_iata": flight['src_iata'],
                                "dest_iata": flight['dest_iata'],
                                "dep_time": flight['dep_time'],
                                "price": flight['price'],
                                "order_time": order['order_time']
                            })
                
                response = {"type": "my_orders_res", "orders": my_list}

            else:
                print(f"⚠️ 未知类型: {req_type}")
                continue

            # 发送回执
            send_packet(conn, response)

    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        conn.close()
        print(f"🔒 连接断开: {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"🚀 假服务器运行中... {HOST}:{PORT}")
    print("------------------------------------------------")

    while True:
        conn, addr = server.accept()
        # 使用线程处理每个客户端，防止界面卡死
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    start_server()