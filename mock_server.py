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
    {"iata": "PEK", "city": "北京", "name": "首都国际机场", "pinyin": "B"},
    {"iata": "PKX", "city": "北京", "name": "大兴国际机场", "pinyin": "B"},
    {"iata": "CAN", "city": "广州", "name": "白云国际机场", "pinyin": "G"},
    {"iata": "HGH", "city": "杭州", "name": "萧山国际机场", "pinyin": "H"},
    {"iata": "NKG", "city": "南京", "name": "禄口国际机场", "pinyin": "N"},
    {"iata": "SHA", "city": "上海", "name": "虹桥国际机场", "pinyin": "S"},
    {"iata": "PVG", "city": "上海", "name": "浦东国际机场", "pinyin": "S"},
    {"iata": "SZX", "city": "深圳", "name": "宝安国际机场", "pinyin": "S"},
    {"iata": "WUH", "city": "武汉", "name": "天河国际机场", "pinyin": "W"},
    {"iata": "XIY", "city": "西安", "name": "咸阳国际机场", "pinyin": "X"}, 
    # 西南地区
    {"iata": "CTU", "city": "成都", "name": "双流国际机场", "pinyin": "C"},
    {"iata": "TFU", "city": "成都", "name": "天府国际机场", "pinyin": "C"},
    {"iata": "CKG", "city": "重庆", "name": "江北国际机场", "pinyin": "C"},
    {"iata": "KMG", "city": "昆明", "name": "长水国际机场", "pinyin": "K"},
    {"iata": "KWE", "city": "贵阳", "name": "龙洞堡国际机场", "pinyin": "G"},

    # 华东地区 (补充)
    {"iata": "XMN", "city": "厦门", "name": "高崎国际机场", "pinyin": "X"},
    {"iata": "FOC", "city": "福州", "name": "长乐国际机场", "pinyin": "F"},
    {"iata": "TAO", "city": "青岛", "name": "胶东国际机场", "pinyin": "Q"},
    {"iata": "TNA", "city": "济南", "name": "遥墙国际机场", "pinyin": "J"},
    {"iata": "HFE", "city": "合肥", "name": "新桥国际机场", "pinyin": "H"},
    {"iata": "NGB", "city": "宁波", "name": "栎社国际机场", "pinyin": "N"},
    {"iata": "WNZ", "city": "温州", "name": "龙湾国际机场", "pinyin": "W"},

    # 华北地区 (补充)
    {"iata": "TSN", "city": "天津", "name": "滨海国际机场", "pinyin": "T"},
    {"iata": "SJW", "city": "石家庄", "name": "正定国际机场", "pinyin": "S"},
    {"iata": "TYN", "city": "太原", "name": "武宿国际机场", "pinyin": "T"},
    {"iata": "HET", "city": "呼和浩特", "name": "白塔国际机场", "pinyin": "H"},

    # 华中地区 (补充)
    {"iata": "CSX", "city": "长沙", "name": "黄花国际机场", "pinyin": "C"},
    {"iata": "CGO", "city": "郑州", "name": "新郑国际机场", "pinyin": "Z"},

    # 东北地区
    {"iata": "DLC", "city": "大连", "name": "周水子国际机场", "pinyin": "D"},
    {"iata": "SHE", "city": "沈阳", "name": "桃仙国际机场", "pinyin": "S"},
    {"iata": "HRB", "city": "哈尔滨", "name": "太平国际机场", "pinyin": "H"},
    {"iata": "CGQ", "city": "长春", "name": "龙嘉国际机场", "pinyin": "C"},

    # 西北地区
    {"iata": "URC", "city": "乌鲁木齐", "name": "地窝堡国际机场", "pinyin": "W"},
    {"iata": "LHW", "city": "兰州", "name": "中川国际机场", "pinyin": "L"},
    {"iata": "INC", "city": "银川", "name": "河东国际机场", "pinyin": "Y"},
    {"iata": "XNN", "city": "西宁", "name": "曹家堡国际机场", "pinyin": "X"},

    # 华南地区 (补充)
    {"iata": "HAK", "city": "海口", "name": "美兰国际机场", "pinyin": "H"},
    {"iata": "SYX", "city": "三亚", "name": "凤凰国际机场", "pinyin": "S"},
    {"iata": "NNG", "city": "南宁", "name": "吴圩国际机场", "pinyin": "N"},
    {"iata": "KWL", "city": "桂林", "name": "两江国际机场", "pinyin": "G"},
    {"iata": "ZUH", "city": "珠海", "name": "金湾机场", "pinyin": "Z"},

    # 虚拟世界
    # --- 明日方舟 (Arknights) ---
    # 龙门 (Lungmen): 虽是移动城邦，但设有飞行器起降平台
    {"iata": "LGM", "city": "龙门", "name": "龙门外环国际空港", "pinyin": "L"},
    # 莱茵生命 (Rhine Lab): 位于哥伦比亚的科技重镇
    {"iata": "RLB", "city": "特里蒙", "name": "莱茵生命总部停机坪", "pinyin": "T"},

    # --- 赛博朋克 2077 (Cyberpunk 2077) ---
    # 夜之城 (Night City): 著名的轨道航空发射中心
    {"iata": "NCX", "city": "夜之城", "name": "轨道航空航天港", "pinyin": "Y"},

    # --- GTA V (侠盗猎车手 5) ---
    # 洛圣都 (Los Santos): 也就是游戏里那个著名的 LSIA
    {"iata": "LSX", "city": "洛圣都", "name": "洛圣都国际机场", "pinyin": "L"},

    # --- 原神 (Genshin Impact) ---
    # 提瓦特大陆虽无喷气机，但枫丹有飞艇技术。
    # 这里假设是“枫丹科学院”下属的运输枢纽
    {"iata": "FNT", "city": "枫丹廷", "name": "安东·罗杰飞行器总站", "pinyin": "F"},

    # --- 崩坏：星穹铁道 (Honkai: Star Rail) ---
    # 仙舟罗浮 (Xianzhou Luofu): 星际航行的港口
    {"iata": "XZL", "city": "仙舟罗浮", "name": "星槎海中枢", "pinyin": "X"},
    # 匹诺康尼 (Penacony): 筑梦边境的入梦关口
    {"iata": "PNY", "city": "匹诺康尼", "name": "白日梦酒店入梦航站", "pinyin": "P"},

    # --- 绝区零 (Zenless Zone Zero) ---
    # 新艾利都 (New Eridu): 用于连接空洞内外的物资运输
    {"iata": "NED", "city": "新艾利都", "name": "空洞调查协会(HIA)空场", "pinyin": "X"},

    # --- 绝地求生 (PUBG) ---
    # 艾伦格 (Erangel): 那个著名的军事基地，虽然已经废弃但代码常用
    {"iata": "SOS", "city": "艾伦格", "name": "索斯诺夫卡军事基地", "pinyin": "A"},
    
    # --- 使命召唤：战区 (Call of Duty: Warzone) ---
    # 维尔丹斯克 (Verdansk): 经典的地图地标
    {"iata": "VDK", "city": "维尔丹斯克", "name": "维尔丹斯克国际机场", "pinyin": "W"},

    {"iata": "HVK", "city": "阿萨拉", "name": "哈夫克航天发射中心", "pinyin": "A"},
    
    # 巴克什 (Bakhshi): 哈夫克总部巴别塔所在地，拥有港口和商务停机坪
    {"iata": "BKS", "city": "阿萨拉", "name": "巴克什哈夫克总部空港", "pinyin": "A"},
    
    # 零号大坝 (Zero Dam): 虽然目前被卫队控制，但假设有战术撤离点
    {"iata": "ZDM", "city": "阿萨拉", "name": "零号大坝战术停机坪", "pinyin": "A"},
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
    },
    # --- 真实世界航线 ---
    {
        "id": 504, "flight_no": "CA4501", 
        "src_iata": "SHA", "dest_iata": "CTU", # 上海虹桥 -> 成都双流
        "dep_time": "2023-12-26 08:30", "arr_time": "2023-12-26 11:45", 
        "price": 1100, "tickets_left": 15
    },
    {
        "id": 505, "flight_no": "ZH9123", 
        "src_iata": "SZX", "dest_iata": "HGH", # 深圳宝安 -> 杭州萧山
        "dep_time": "2023-12-26 10:15", "arr_time": "2023-12-26 12:20", 
        "price": 950, "tickets_left": 8
    },
    {
        "id": 506, "flight_no": "HU7321", 
        "src_iata": "XIY", "dest_iata": "URC", # 西安咸阳 -> 乌鲁木齐地窝堡
        "dep_time": "2023-12-26 13:00", "arr_time": "2023-12-26 17:15", 
        "price": 1500, "tickets_left": 0 # 热门航线售罄
    },
    {
        "id": 507, "flight_no": "MF8001", 
        "src_iata": "XMN", "dest_iata": "PKX", # 厦门高崎 -> 北京大兴
        "dep_time": "2023-12-26 16:20", "arr_time": "2023-12-26 19:00", 
        "price": 1300, "tickets_left": 25
    },
    {
        "id": 508, "flight_no": "3U8888", 
        "src_iata": "TFU", "dest_iata": "LHW", # 成都天府 -> 兰州中川
        "dep_time": "2023-12-26 07:50", "arr_time": "2023-12-26 09:20", 
        "price": 600, "tickets_left": 18
    },

    # --- 虚拟世界航线 (Fun Routes) ---
    {
        # 赛博朋克 -> GTA (跨游戏联动)
        "id": 509, "flight_no": "NC2077", 
        "src_iata": "NCX", "dest_iata": "LSX", # 夜之城 -> 洛圣都
        "dep_time": "2023-12-26 22:00", "arr_time": "2023-12-26 23:30", 
        "price": 2000, "tickets_left": 50
    },
    {
        # 明日方舟 (龙门 -> 莱茵生命)
        "id": 510, "flight_no": "AK0723", 
        "src_iata": "LGM", "dest_iata": "RLB", # 龙门 -> 特里蒙
        "dep_time": "2023-12-26 09:00", "arr_time": "2023-12-26 15:00", 
        "price": 4500, "tickets_left": 3
    },
    {
        # 崩坏：星穹铁道 (星际航行)
        "id": 511, "flight_no": "SR1001", 
        "src_iata": "XZL", "dest_iata": "PNY", # 仙舟罗浮 -> 匹诺康尼
        "dep_time": "2023-12-26 10:00", "arr_time": "2023-12-26 18:00", 
        "price": 9999, "tickets_left": 1 # 仅剩一张信用点票
    },
    {
        # 绝地求生 -> 战区 (硬核军事航班)
        "id": 512, "flight_no": "C130", 
        "src_iata": "SOS", "dest_iata": "VDK", # 艾伦格 -> 维尔丹斯克
        "dep_time": "2023-12-26 04:00", "arr_time": "2023-12-26 06:00", 
        "price": 100, "tickets_left": 99 # 运输机座位充足
    },
    {
        # 原神 -> 绝区零 (米哈游宇宙)
        "id": 513, "flight_no": "HYV520", 
        "src_iata": "FNT", "dest_iata": "NED", # 枫丹 -> 新艾利都
        "dep_time": "2023-12-26 14:00", "arr_time": "2023-12-26 16:30", 
        "price": 648, "tickets_left": 0 # 648航班已售罄
    },
    {
        # 航线：航天基地 -> 巴克什
        # 背景：从火箭发射回收区运送曼德尔砖样本回总部巴别塔
        "id": 514, "flight_no": "GTI-01", 
        "src_iata": "HVK", "dest_iata": "BKS", 
        "dep_time": "2023-12-26 06:00", "arr_time": "2023-12-26 06:45", # 同城短途飞行，45分钟
        "price": 3000, "tickets_left": 4 # 仅限高级干员
    },
    {
        # 航线：巴克什 -> 航天基地 (返程补给)
        "id": 515, "flight_no": "GTI-02",
        "src_iata": "BKS", "dest_iata": "HVK",
        "dep_time": "2023-12-26 18:00", "arr_time": "2023-12-26 18:45",
        "price": 3000, "tickets_left": 10
    },
    {
        # 航线：巴克什 -> 零号大坝 (危险任务：深入卫队控制区)
        "id": 516, "flight_no": "MANDEL-X",
        "src_iata": "BKS", "dest_iata": "ZDM",
        "dep_time": "2023-12-26 23:00", "arr_time": "2023-12-26 23:30",
        "price": 5000, "tickets_left": 1 # 极密任务
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