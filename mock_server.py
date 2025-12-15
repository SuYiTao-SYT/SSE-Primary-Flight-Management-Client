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
    {"iata_code": "PEK", "city_name": "北京", "airport_name": "首都国际机场", "city_pinyin":  "B"},
    {"iata_code": "PKX", "city_name": "北京", "airport_name": "大兴国际机场", "city_pinyin":  "B"},
    {"iata_code": "CAN", "city_name": "广州", "airport_name": "白云国际机场", "city_pinyin":  "G"},
    {"iata_code": "HGH", "city_name": "杭州", "airport_name": "萧山国际机场", "city_pinyin":  "H"},
    {"iata_code": "NKG", "city_name": "南京", "airport_name": "禄口国际机场", "city_pinyin":  "N"},
    {"iata_code": "SHA", "city_name": "上海", "airport_name": "虹桥国际机场", "city_pinyin":  "S"},
    {"iata_code": "PVG", "city_name": "上海", "airport_name": "浦东国际机场", "city_pinyin":  "S"},
    {"iata_code": "SZX", "city_name": "深圳", "airport_name": "宝安国际机场", "city_pinyin":  "S"},
    {"iata_code": "WUH", "city_name": "武汉", "airport_name": "天河国际机场", "city_pinyin":  "W"},
    {"iata_code": "XIY", "city_name": "西安", "airport_name": "咸阳国际机场", "city_pinyin":  "X"}, 
    # 西南地区
    {"iata_code": "CTU", "city_name": "成都", "airport_name": "双流国际机场", "city_pinyin":  "C"},
    {"iata_code": "TFU", "city_name": "成都", "airport_name": "天府国际机场", "city_pinyin":  "C"},
    {"iata_code": "CKG", "city_name": "重庆", "airport_name": "江北国际机场", "city_pinyin":  "C"},
    {"iata_code": "KMG", "city_name": "昆明", "airport_name": "长水国际机场", "city_pinyin":  "K"},
    {"iata_code": "KWE", "city_name": "贵阳", "airport_name": "龙洞堡国际机场", "city_pinyin":  "G"},

    # 华东地区 (补充)
    {"iata_code": "XMN", "city_name": "厦门", "airport_name": "高崎国际机场", "city_pinyin":  "X"},
    {"iata_code": "FOC", "city_name": "福州", "airport_name": "长乐国际机场", "city_pinyin":  "F"},
    {"iata_code": "TAO", "city_name": "青岛", "airport_name": "胶东国际机场", "city_pinyin":  "Q"},
    {"iata_code": "TNA", "city_name": "济南", "airport_name": "遥墙国际机场", "city_pinyin":  "J"},
    {"iata_code": "HFE", "city_name": "合肥", "airport_name": "新桥国际机场", "city_pinyin":  "H"},
    {"iata_code": "NGB", "city_name": "宁波", "airport_name": "栎社国际机场", "city_pinyin":  "N"},
    {"iata_code": "WNZ", "city_name": "温州", "airport_name": "龙湾国际机场", "city_pinyin":  "W"},

    # 华北地区 (补充)
    {"iata_code": "TSN", "city_name": "天津", "airport_name": "滨海国际机场", "city_pinyin":  "T"},
    {"iata_code": "SJW", "city_name": "石家庄", "airport_name": "正定国际机场", "city_pinyin":  "S"},
    {"iata_code": "TYN", "city_name": "太原", "airport_name": "武宿国际机场", "city_pinyin":  "T"},
    {"iata_code": "HET", "city_name": "呼和浩特", "airport_name": "白塔国际机场", "city_pinyin":  "H"},

    # 华中地区 (补充)
    {"iata_code": "CSX", "city_name": "长沙", "airport_name": "黄花国际机场", "city_pinyin":  "C"},
    {"iata_code": "CGO", "city_name": "郑州", "airport_name": "新郑国际机场", "city_pinyin":  "Z"},

    # 东北地区
    {"iata_code": "DLC", "city_name": "大连", "airport_name": "周水子国际机场", "city_pinyin":  "D"},
    {"iata_code": "SHE", "city_name": "沈阳", "airport_name": "桃仙国际机场", "city_pinyin":  "S"},
    {"iata_code": "HRB", "city_name": "哈尔滨", "airport_name": "太平国际机场", "city_pinyin":  "H"},
    {"iata_code": "CGQ", "city_name": "长春", "airport_name": "龙嘉国际机场", "city_pinyin":  "C"},

    # 西北地区
    {"iata_code": "URC", "city_name": "乌鲁木齐", "airport_name": "地窝堡国际机场", "city_pinyin":  "W"},
    {"iata_code": "LHW", "city_name": "兰州", "airport_name": "中川国际机场", "city_pinyin":  "L"},
    {"iata_code": "INC", "city_name": "银川", "airport_name": "河东国际机场", "city_pinyin":  "Y"},
    {"iata_code": "XNN", "city_name": "西宁", "airport_name": "曹家堡国际机场", "city_pinyin":  "X"},

    # 华南地区 (补充)
    {"iata_code": "HAK", "city_name": "海口", "airport_name": "美兰国际机场", "city_pinyin":  "H"},
    {"iata_code": "SYX", "city_name": "三亚", "airport_name": "凤凰国际机场", "city_pinyin":  "S"},
    {"iata_code": "NNG", "city_name": "南宁", "airport_name": "吴圩国际机场", "city_pinyin":  "N"},
    {"iata_code": "KWL", "city_name": "桂林", "airport_name": "两江国际机场", "city_pinyin":  "G"},
    {"iata_code": "ZUH", "city_name": "珠海", "airport_name": "金湾机场", "city_pinyin":  "Z"},

    # 虚拟世界
    # --- 明日方舟 (Arknights) ---
    # 龙门 (Lungmen): 虽是移动城邦，但设有飞行器起降平台
    {"iata_code": "LGM", "city_name": "龙门", "airport_name": "龙门外环国际空港", "city_pinyin":  "L"},
    # 莱茵生命 (Rhine Lab): 位于哥伦比亚的科技重镇
    {"iata_code": "RLB", "city_name": "特里蒙", "airport_name": "莱茵生命总部停机坪", "city_pinyin":  "T"},
    # --- 维多利亚 (Victoria) ---
    # 伦蒂尼姆 (Londinium): 蒸汽甲胄与工业的中心
    {"iata_code": "LND", "city_name": "伦蒂尼姆", "airport_name": "伦蒂尼姆皇家飞艇停泊港", "city_pinyin":  "L"},
    
    # --- 谢拉格 (Kjerag) ---
    # 喀兰贸易 (Karlan): 银灰掌控的雪境门户
    {"iata_code": "KJR", "city_name": "谢拉格", "airport_name": "曼德尔城喀兰贸易空港", "city_pinyin":  "X"},
    
    # --- 炎国 (Yan) ---
    # 玉门 (Yumen): 边防重镇，对抗邪魔的前线
    {"iata_code": "YUM", "city_name": "玉门", "airport_name": "玉门擂台飞行基地", "city_pinyin":  "Y"},
    # 尚蜀 (Shangshu): 逍遥自在的旅游城市
    {"iata_code": "SHS", "city_name": "尚蜀", "airport_name": "尚蜀山城云端渡口", "city_pinyin":  "S"},

    # --- 拉特兰 (Laterano) ---
    # 圣城 (Sancta city_name): 铳与信仰之国
    {"iata_code": "LTR", "city_name": "拉特兰", "airport_name": "圣殿第一公证所停机坪", "city_pinyin":  "L"},

    # --- 伊比利亚 (Iberia) ---
    # 盐风城 (Sal Viento): 虽已没落，但仍有审判庭的据点
    {"iata_code": "SVT", "city_name": "伊比利亚", "airport_name": "盐风城审判庭临时起降点", "city_pinyin":  "Y"},

    # --- 赛博朋克 2077 (Cyberpunk 2077) ---
    # 夜之城 (Night city_name): 著名的轨道航空发射中心
    {"iata_code": "NCX", "city_name": "夜之城", "airport_name": "轨道航空航天港", "city_pinyin":  "Y"},

    # --- GTA V (侠盗猎车手 5) ---
    # 洛圣都 (Los Santos): 也就是游戏里那个著名的 LSIA
    {"iata_code": "LSX", "city_name": "洛圣都", "airport_name": "洛圣都国际机场", "city_pinyin":  "L"},

    # --- 原神 (Genshin Impact) ---
    # 提瓦特大陆虽无喷气机，但枫丹有飞艇技术。
    # 这里假设是“枫丹科学院”下属的运输枢纽
    {"iata_code": "FNT", "city_name": "枫丹廷", "airport_name": "安东·罗杰飞行器总站", "city_pinyin":  "F"},

    # --- 崩坏：星穹铁道 (Honkai: Star Rail) ---
    # 仙舟罗浮 (Xianzhou Luofu): 星际航行的港口
    {"iata_code": "XZL", "city_name": "仙舟罗浮", "airport_name": "星槎海中枢", "city_pinyin":  "X"},
    # 匹诺康尼 (Penacony): 筑梦边境的入梦关口
    {"iata_code": "PNY", "city_name": "匹诺康尼", "airport_name": "白日梦酒店入梦航站", "city_pinyin":  "P"},

    # --- 绝区零 (Zenless Zone Zero) ---
    # 新艾利都 (New Eridu): 用于连接空洞内外的物资运输
    {"iata_code": "NED", "city_name": "新艾利都", "airport_name": "空洞调查协会(HIA)空场", "city_pinyin":  "X"},

    # --- 绝地求生 (PUBG) ---
    # 艾伦格 (Erangel): 那个著名的军事基地，虽然已经废弃但代码常用
    {"iata_code": "SOS", "city_name": "艾伦格", "airport_name": "索斯诺夫卡军事基地", "city_pinyin":  "A"},
    
    # --- 使命召唤：战区 (Call of Duty: Warzone) ---
    # 维尔丹斯克 (Verdansk): 经典的地图地标
    {"iata_code": "VDK", "city_name": "维尔丹斯克", "airport_name": "维尔丹斯克国际机场", "city_pinyin":  "W"},

    {"iata_code": "HVK", "city_name": "阿萨拉", "airport_name": "哈夫克航天发射中心", "city_pinyin":  "A"},
    
    # 巴克什 (Bakhshi): 哈夫克总部巴别塔所在地，拥有港口和商务停机坪
    {"iata_code": "BKS", "city_name": "阿萨拉", "airport_name": "巴别塔总部空港", "city_pinyin":  "A"},
    
    # 零号大坝 (Zero Dam): 虽然目前被卫队控制，但假设有战术撤离点
    {"iata_code": "ZDM", "city_name": "阿萨拉", "airport_name": "零号大坝战术停机坪", "city_pinyin":  "A"},
]

# 3. 模拟数据库：航班表 (包含余票 tickets_left)
flights_db = [
    {
        "id": 501, "flight_no": "CA1501", 
        "src_iata": "PEK", "dest_iata": "SHA", 
        "dep_time": "2025-12-25 08:00", "arr_time": "2025-12-25 10:30", 
        "price": 800, "tickets_left": 5
    },
    {
        "id": 502, "flight_no": "MU5123", 
        "src_iata": "PKX", "dest_iata": "PVG", 
        "dep_time": "2025-12-25 09:00", "arr_time": "2025-12-25 11:30", 
        "price": 750, "tickets_left": 0 # 售罄测试
    },
    {
        "id": 503, "flight_no": "CZ3001", 
        "src_iata": "CAN", "dest_iata": "PEK", 
        "dep_time": "2025-12-26 14:00", "arr_time": "2025-12-26 17:00", 
        "price": 1200, "tickets_left": 20
    },
    # --- 真实世界航线 ---
    {
        "id": 504, "flight_no": "CA4501", 
        "src_iata": "SHA", "dest_iata": "CTU", # 上海虹桥 -> 成都双流
        "dep_time": "2025-12-26 08:30", "arr_time": "2025-12-26 11:45", 
        "price": 1100, "tickets_left": 15
    },
    {
        "id": 505, "flight_no": "ZH9123", 
        "src_iata": "SZX", "dest_iata": "HGH", # 深圳宝安 -> 杭州萧山
        "dep_time": "2025-12-26 10:15", "arr_time": "2025-12-26 12:20", 
        "price": 950, "tickets_left": 8
    },
    {
        "id": 506, "flight_no": "HU7321", 
        "src_iata": "XIY", "dest_iata": "URC", # 西安咸阳 -> 乌鲁木齐地窝堡
        "dep_time": "2025-12-26 13:00", "arr_time": "2025-12-26 17:15", 
        "price": 1500, "tickets_left": 0 # 热门航线售罄
    },
    {
        "id": 507, "flight_no": "MF8001", 
        "src_iata": "XMN", "dest_iata": "PKX", # 厦门高崎 -> 北京大兴
        "dep_time": "2025-12-26 16:20", "arr_time": "2025-12-26 19:00", 
        "price": 1300, "tickets_left": 25
    },
    {
        "id": 508, "flight_no": "3U8888", 
        "src_iata": "TFU", "dest_iata": "LHW", # 成都天府 -> 兰州中川
        "dep_time": "2025-12-26 07:50", "arr_time": "2025-12-26 09:20", 
        "price": 600, "tickets_left": 18
    },

    # --- 虚拟世界航线 (Fun Routes) ---
    {
        # 赛博朋克 -> GTA (跨游戏联动)
        "id": 509, "flight_no": "NC2077", 
        "src_iata": "NCX", "dest_iata": "LSX", # 夜之城 -> 洛圣都
        "dep_time": "2025-12-26 22:00", "arr_time": "2025-12-26 23:30", 
        "price": 2000, "tickets_left": 50
    },
    {
        # 明日方舟 (龙门 -> 莱茵生命)
        "id": 510, "flight_no": "AK0723", 
        "src_iata": "LGM", "dest_iata": "RLB", # 龙门 -> 特里蒙
        "dep_time": "2025-12-26 09:00", "arr_time": "2025-12-26 15:00", 
        "price": 4500, "tickets_left": 3
    },
    {
        # 崩坏：星穹铁道 (星际航行)
        "id": 511, "flight_no": "SR1001", 
        "src_iata": "XZL", "dest_iata": "PNY", # 仙舟罗浮 -> 匹诺康尼
        "dep_time": "2025-12-26 10:00", "arr_time": "2025-12-26 18:00", 
        "price": 9999, "tickets_left": 1 # 仅剩一张信用点票
    },
    {
        # 绝地求生 -> 战区 (硬核军事航班)
        "id": 512, "flight_no": "C130", 
        "src_iata": "SOS", "dest_iata": "VDK", # 艾伦格 -> 维尔丹斯克
        "dep_time": "2025-12-26 04:00", "arr_time": "2025-12-26 06:00", 
        "price": 100, "tickets_left": 99 # 运输机座位充足
    },
    {
        # 原神 -> 绝区零 (米哈游宇宙)
        "id": 513, "flight_no": "HYV520", 
        "src_iata": "FNT", "dest_iata": "NED", # 枫丹 -> 新艾利都
        "dep_time": "2025-12-26 14:00", "arr_time": "2025-12-26 16:30", 
        "price": 648, "tickets_left": 0 # 648航班已售罄
    },
    {
        # 航线：航天基地 -> 巴克什
        # 背景：从火箭发射回收区运送曼德尔砖样本回总部巴别塔
        "id": 514, "flight_no": "GTI-01", 
        "src_iata": "HVK", "dest_iata": "BKS", 
        "dep_time": "2025-12-26 06:00", "arr_time": "2025-12-26 06:45", # 同城短途飞行，45分钟
        "price": 3000, "tickets_left": 4 # 仅限高级干员
    },
    {
        # 航线：巴克什 -> 航天基地 (返程补给)
        "id": 515, "flight_no": "GTI-02",
        "src_iata": "BKS", "dest_iata": "HVK",
        "dep_time": "2025-12-26 18:00", "arr_time": "2025-12-26 18:45",
        "price": 3000, "tickets_left": 10
    },
    {
        # 航线：巴克什 -> 零号大坝 (危险任务：深入卫队控制区)
        "id": 516, "flight_no": "MANDEL-X",
        "src_iata": "BKS", "dest_iata": "ZDM",
        "dep_time": "2025-12-26 23:00", "arr_time": "2025-12-26 23:30",
        "price": 5001, "tickets_left": 1 # 极密任务
    },

    ##新增
    # 北京(PEK) <-> 上海(SHA) - 商务干线
    {
        "id": 601, "flight_no": "CA1501", 
        "src_iata": "PEK", "dest_iata": "SHA", 
        "dep_time": "2025-12-20 08:00", "arr_time": "2025-12-20 10:15", 
        "price": 1200, "tickets_left": 20
    },
    {
        "id": 602, "flight_no": "MU5100", 
        "src_iata": "SHA", "dest_iata": "PEK", 
        "dep_time": "2025-12-20 14:00", "arr_time": "2025-12-20 16:20", 
        "price": 1150, "tickets_left": 5
    },
    # 广州(CAN) -> 成都(TFU)
    {
        "id": 603, "flight_no": "CZ3401", 
        "src_iata": "CAN", "dest_iata": "TFU", 
        "dep_time": "2025-12-21 09:30", "arr_time": "2025-12-21 12:00", 
        "price": 980, "tickets_left": 45
    },
    # 深圳(SZX) -> 乌鲁木齐(URC) - 长途
    {
        "id": 604, "flight_no": "ZH9881", 
        "src_iata": "SZX", "dest_iata": "URC", 
        "dep_time": "2025-12-22 07:00", "arr_time": "2025-12-22 12:30", 
        "price": 2400, "tickets_left": 10
    },

    # ==========================================
    # 2. 阿萨拉战区 (三角洲行动 Delta Force)
    # 特点：同城(city_name=阿萨拉)，短途，战术编号
    # ==========================================
    # 航天基地(HVK) -> 巴别塔总部(BKS) - 物资运送
    {
        "id": 610, "flight_no": "GTI-Alpha", 
        "src_iata": "HVK", "dest_iata": "BKS", 
        "dep_time": "2025-12-24 06:00", "arr_time": "2025-12-24 06:40", 
        "price": 500, "tickets_left": 2 # 内部专机
    },
    # 巴别塔总部(BKS) -> 零号大坝(ZDM) - 快速反应
    {
        "id": 611, "flight_no": "MANDEL-01", 
        "src_iata": "BKS", "dest_iata": "ZDM", 
        "dep_time": "2025-12-24 23:30", "arr_time": "2025-12-25 00:00", 
        "price": 8000, "tickets_left": 0 # 任务已满员
    },
    # 零号大坝(ZDM) -> 航天基地(HVK) - 撤离航班
    {
        "id": 612, "flight_no": "EVAC-99", 
        "src_iata": "ZDM", "dest_iata": "HVK", 
        "dep_time": "2025-12-25 04:00", "arr_time": "2025-12-25 04:50", 
        "price": 100, "tickets_left": 50
    },

    # ==========================================
    # 3. 二次元/科幻 热门航线
    # ==========================================
    # 夜之城(NCX) -> 洛圣都(LSX) - 圣诞逃亡
    {
        "id": 620, "flight_no": "NC-2077", 
        "src_iata": "NCX", "dest_iata": "LSX", 
        "dep_time": "2025-12-25 20:00", "arr_time": "2025-12-25 21:30", 
        "price": 2000, "tickets_left": 10
    },
    # 仙舟罗浮(XZL) -> 匹诺康尼(PNY) - 跨年庆典
    {
        "id": 621, "flight_no": "IPC-Star", 
        "src_iata": "XZL", "dest_iata": "PNY", 
        "dep_time": "2025-12-31 22:00", "arr_time": "2025-12-31 23:59", 
        "price": 9999, "tickets_left": 1
    },
    # 龙门(LGM) -> 维尔丹斯克(VDK) - 极其危险的航线
    {
        "id": 622, "flight_no": "LGD-WAR", 
        "src_iata": "LGM", "dest_iata": "VDK", 
        "dep_time": "2025-12-28 10:00", "arr_time": "2025-12-28 16:00", 
        "price": 300, "tickets_left": 100 # 没人敢去
    },

    # ==========================================
    # 4. 循环生成的日常航班 (填补日期空白)
    # ==========================================
    # 12月26日 - 节礼日航班
    {
        "id": 630, "flight_no": "CA1502", 
        "src_iata": "SHA", "dest_iata": "PEK", 
        "dep_time": "2025-12-26 18:00", "arr_time": "2025-12-26 20:30", 
        "price": 900, "tickets_left": 30
    },
    {
        "id": 631, "flight_no": "3U8666", 
        "src_iata": "CTU", "dest_iata": "LHW", # 成都 -> 兰州
        "dep_time": "2025-12-26 12:00", "arr_time": "2025-12-26 13:30", 
        "price": 600, "tickets_left": 12
    },
    
    # 12月28日 - 周末航班
    {
        "id": 640, "flight_no": "GTI-Beta", 
        "src_iata": "HVK", "dest_iata": "ZDM", # 阿萨拉内部
        "dep_time": "2025-12-28 09:00", "arr_time": "2025-12-28 09:40", 
        "price": 4500, "tickets_left": 3
    },
    {
        "id": 641, "flight_no": "HYV-ZZZ", 
        "src_iata": "NED", "dest_iata": "FNT", # 新艾利都 -> 枫丹
        "dep_time": "2025-12-28 15:00", "arr_time": "2025-12-28 17:30", 
        "price": 648, "tickets_left": 64
    },

    # 12月30日 - 年末返程
    {
        "id": 650, "flight_no": "HU7777", 
        "src_iata": "HAK", "dest_iata": "PEK", # 海口 -> 北京
        "dep_time": "2025-12-30 13:00", "arr_time": "2025-12-30 16:30", 
        "price": 1800, "tickets_left": 8
    },
    {
        "id": 651, "flight_no": "MU2026", 
        "src_iata": "XIY", "dest_iata": "SHA", # 西安 -> 上海
        "dep_time": "2025-12-30 19:00", "arr_time": "2025-12-30 21:15", 
        "price": 1050, "tickets_left": 18
    },
        # --- 2025-12-20 ---
    {"id": 600, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-20 08:00", "arr_time": "2025-12-20 10:15", "price": 1200, "tickets_left": 5},
    {"id": 601, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-20 13:00", "arr_time": "2025-12-20 15:20", "price": 1100, "tickets_left": 5},
    {"id": 602, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-20 18:30", "arr_time": "2025-12-20 20:45", "price": 1000, "tickets_left": 5},
    {"id": 603, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-20 21:00", "arr_time": "2025-12-20 23:15", "price": 950, "tickets_left": 5},
    {"id": 604, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-20 06:00", "arr_time": "2025-12-20 06:40", "price": 500, "tickets_left": 3},
    {"id": 605, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-20 18:00", "arr_time": "2025-12-20 18:40", "price": 500, "tickets_left": 3},
    {"id": 606, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-20 23:00", "arr_time": "2025-12-20 23:30", "price": 3000, "tickets_left": 3},
    {"id": 607, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-20 23:00", "arr_time": "2025-12-20 04:00", "price": 1500, "tickets_left": 50},
    {"id": 608, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-20 10:00", "arr_time": "2025-12-20 11:30", "price": 800, "tickets_left": 50},
    {"id": 609, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-20 08:00", "arr_time": "2025-12-20 12:00", "price": 2500, "tickets_left": 10},
    {"id": 610, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-20 09:00", "arr_time": "2025-12-20 15:00", "price": 3000, "tickets_left": 10},
    {"id": 611, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-20 12:00", "arr_time": "2025-12-20 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-21 ---
    {"id": 612, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-21 08:00", "arr_time": "2025-12-21 10:15", "price": 1200, "tickets_left": 5},
    {"id": 613, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-21 13:00", "arr_time": "2025-12-21 15:20", "price": 1100, "tickets_left": 5},
    {"id": 614, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-21 18:30", "arr_time": "2025-12-21 20:45", "price": 1000, "tickets_left": 5},
    {"id": 615, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-21 21:00", "arr_time": "2025-12-21 23:15", "price": 950, "tickets_left": 5},
    {"id": 616, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-21 06:00", "arr_time": "2025-12-21 06:40", "price": 500, "tickets_left": 3},
    {"id": 617, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-21 18:00", "arr_time": "2025-12-21 18:40", "price": 500, "tickets_left": 3},
    {"id": 618, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-21 23:00", "arr_time": "2025-12-21 23:30", "price": 3000, "tickets_left": 3},
    {"id": 619, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-21 23:00", "arr_time": "2025-12-21 04:00", "price": 1500, "tickets_left": 50},
    {"id": 620, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-21 10:00", "arr_time": "2025-12-21 11:30", "price": 800, "tickets_left": 50},
    {"id": 621, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-21 08:00", "arr_time": "2025-12-21 12:00", "price": 2500, "tickets_left": 10},
    {"id": 622, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-21 09:00", "arr_time": "2025-12-21 15:00", "price": 3000, "tickets_left": 10},
    {"id": 623, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-21 12:00", "arr_time": "2025-12-21 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-22 ---
    {"id": 624, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-22 08:00", "arr_time": "2025-12-22 10:15", "price": 1200, "tickets_left": 20},
    {"id": 625, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-22 13:00", "arr_time": "2025-12-22 15:20", "price": 1100, "tickets_left": 20},
    {"id": 626, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-22 18:30", "arr_time": "2025-12-22 20:45", "price": 1000, "tickets_left": 20},
    {"id": 627, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-22 21:00", "arr_time": "2025-12-22 23:15", "price": 950, "tickets_left": 20},
    {"id": 628, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-22 06:00", "arr_time": "2025-12-22 06:40", "price": 500, "tickets_left": 3},
    {"id": 629, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-22 18:00", "arr_time": "2025-12-22 18:40", "price": 500, "tickets_left": 3},
    {"id": 630, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-22 23:00", "arr_time": "2025-12-22 23:30", "price": 3000, "tickets_left": 3},
    {"id": 631, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-22 23:00", "arr_time": "2025-12-22 04:00", "price": 1500, "tickets_left": 50},
    {"id": 632, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-22 10:00", "arr_time": "2025-12-22 11:30", "price": 800, "tickets_left": 50},
    {"id": 633, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-22 08:00", "arr_time": "2025-12-22 12:00", "price": 2500, "tickets_left": 10},
    {"id": 634, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-22 09:00", "arr_time": "2025-12-22 15:00", "price": 3000, "tickets_left": 10},
    {"id": 635, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-22 12:00", "arr_time": "2025-12-22 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-23 ---
    {"id": 636, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-23 08:00", "arr_time": "2025-12-23 10:15", "price": 1200, "tickets_left": 20},
    {"id": 637, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-23 13:00", "arr_time": "2025-12-23 15:20", "price": 1100, "tickets_left": 20},
    {"id": 638, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-23 18:30", "arr_time": "2025-12-23 20:45", "price": 1000, "tickets_left": 20},
    {"id": 639, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-23 21:00", "arr_time": "2025-12-23 23:15", "price": 950, "tickets_left": 20},
    {"id": 640, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-23 06:00", "arr_time": "2025-12-23 06:40", "price": 500, "tickets_left": 3},
    {"id": 641, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-23 18:00", "arr_time": "2025-12-23 18:40", "price": 500, "tickets_left": 3},
    {"id": 642, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-23 23:00", "arr_time": "2025-12-23 23:30", "price": 3000, "tickets_left": 3},
    {"id": 643, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-23 23:00", "arr_time": "2025-12-23 04:00", "price": 1500, "tickets_left": 50},
    {"id": 644, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-23 10:00", "arr_time": "2025-12-23 11:30", "price": 800, "tickets_left": 50},
    {"id": 645, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-23 08:00", "arr_time": "2025-12-23 12:00", "price": 2500, "tickets_left": 10},
    {"id": 646, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-23 09:00", "arr_time": "2025-12-23 15:00", "price": 3000, "tickets_left": 10},
    {"id": 647, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-23 12:00", "arr_time": "2025-12-23 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-24 ---
    {"id": 648, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-24 08:00", "arr_time": "2025-12-24 10:15", "price": 1800, "tickets_left": 20},
    {"id": 649, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-24 13:00", "arr_time": "2025-12-24 15:20", "price": 1650, "tickets_left": 20},
    {"id": 650, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-24 18:30", "arr_time": "2025-12-24 20:45", "price": 1500, "tickets_left": 20},
    {"id": 651, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-24 21:00", "arr_time": "2025-12-24 23:15", "price": 1425, "tickets_left": 20},
    {"id": 652, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-24 06:00", "arr_time": "2025-12-24 06:40", "price": 500, "tickets_left": 3},
    {"id": 653, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-24 18:00", "arr_time": "2025-12-24 18:40", "price": 500, "tickets_left": 3},
    {"id": 654, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-24 23:00", "arr_time": "2025-12-24 23:30", "price": 3000, "tickets_left": 3},
    {"id": 655, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-24 23:00", "arr_time": "2025-12-24 04:00", "price": 1500, "tickets_left": 50},
    {"id": 656, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-24 10:00", "arr_time": "2025-12-24 11:30", "price": 800, "tickets_left": 50},
    {"id": 657, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-24 08:00", "arr_time": "2025-12-24 12:00", "price": 2500, "tickets_left": 10},
    {"id": 658, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-24 09:00", "arr_time": "2025-12-24 15:00", "price": 3000, "tickets_left": 10},
    {"id": 659, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-24 12:00", "arr_time": "2025-12-24 16:00", "price": 1200, "tickets_left": 10},
    {"id": 660, "flight_no": "NC-2077", "src_iata": "NCX", "dest_iata": "LSX", "dep_time": "2025-12-24 20:00", "arr_time": "2025-12-24 21:30", "price": 2000, "tickets_left": 0},
    {"id": 661, "flight_no": "SR-1001", "src_iata": "XZL", "dest_iata": "PNY", "dep_time": "2025-12-24 10:00", "arr_time": "2025-12-24 18:00", "price": 9999, "tickets_left": 0},
    # --- 2025-12-25 ---
    {"id": 662, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-25 08:00", "arr_time": "2025-12-25 10:15", "price": 1800, "tickets_left": 20},
    {"id": 663, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-25 13:00", "arr_time": "2025-12-25 15:20", "price": 1650, "tickets_left": 20},
    {"id": 664, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-25 18:30", "arr_time": "2025-12-25 20:45", "price": 1500, "tickets_left": 20},
    {"id": 665, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-25 21:00", "arr_time": "2025-12-25 23:15", "price": 1425, "tickets_left": 20},
    {"id": 666, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-25 06:00", "arr_time": "2025-12-25 06:40", "price": 500, "tickets_left": 3},
    {"id": 667, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-25 18:00", "arr_time": "2025-12-25 18:40", "price": 500, "tickets_left": 3},
    {"id": 668, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-25 23:00", "arr_time": "2025-12-25 23:30", "price": 3000, "tickets_left": 3},
    {"id": 669, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-25 23:00", "arr_time": "2025-12-25 04:00", "price": 1500, "tickets_left": 50},
    {"id": 670, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-25 10:00", "arr_time": "2025-12-25 11:30", "price": 800, "tickets_left": 50},
    {"id": 671, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-25 08:00", "arr_time": "2025-12-25 12:00", "price": 2500, "tickets_left": 10},
    {"id": 672, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-25 09:00", "arr_time": "2025-12-25 15:00", "price": 3000, "tickets_left": 10},
    {"id": 673, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-25 12:00", "arr_time": "2025-12-25 16:00", "price": 1200, "tickets_left": 10},
    {"id": 674, "flight_no": "NC-2077", "src_iata": "NCX", "dest_iata": "LSX", "dep_time": "2025-12-25 20:00", "arr_time": "2025-12-25 21:30", "price": 2000, "tickets_left": 0},
    {"id": 675, "flight_no": "SR-1001", "src_iata": "XZL", "dest_iata": "PNY", "dep_time": "2025-12-25 10:00", "arr_time": "2025-12-25 18:00", "price": 9999, "tickets_left": 0},
    # --- 2025-12-26 ---
    {"id": 676, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-26 08:00", "arr_time": "2025-12-26 10:15", "price": 1200, "tickets_left": 20},
    {"id": 677, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-26 13:00", "arr_time": "2025-12-26 15:20", "price": 1100, "tickets_left": 20},
    {"id": 678, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-26 18:30", "arr_time": "2025-12-26 20:45", "price": 1000, "tickets_left": 20},
    {"id": 679, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-26 21:00", "arr_time": "2025-12-26 23:15", "price": 950, "tickets_left": 20},
    {"id": 680, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-26 06:00", "arr_time": "2025-12-26 06:40", "price": 500, "tickets_left": 3},
    {"id": 681, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-26 18:00", "arr_time": "2025-12-26 18:40", "price": 500, "tickets_left": 3},
    {"id": 682, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-26 23:00", "arr_time": "2025-12-26 23:30", "price": 3000, "tickets_left": 3},
    {"id": 683, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-26 23:00", "arr_time": "2025-12-26 04:00", "price": 1500, "tickets_left": 50},
    {"id": 684, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-26 10:00", "arr_time": "2025-12-26 11:30", "price": 800, "tickets_left": 50},
    {"id": 685, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-26 08:00", "arr_time": "2025-12-26 12:00", "price": 2500, "tickets_left": 10},
    {"id": 686, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-26 09:00", "arr_time": "2025-12-26 15:00", "price": 3000, "tickets_left": 10},
    {"id": 687, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-26 12:00", "arr_time": "2025-12-26 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-27 ---
    {"id": 688, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-27 08:00", "arr_time": "2025-12-27 10:15", "price": 1200, "tickets_left": 5},
    {"id": 689, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-27 13:00", "arr_time": "2025-12-27 15:20", "price": 1100, "tickets_left": 5},
    {"id": 690, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-27 18:30", "arr_time": "2025-12-27 20:45", "price": 1000, "tickets_left": 5},
    {"id": 691, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-27 21:00", "arr_time": "2025-12-27 23:15", "price": 950, "tickets_left": 5},
    {"id": 692, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-27 06:00", "arr_time": "2025-12-27 06:40", "price": 500, "tickets_left": 3},
    {"id": 693, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-27 18:00", "arr_time": "2025-12-27 18:40", "price": 500, "tickets_left": 3},
    {"id": 694, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-27 23:00", "arr_time": "2025-12-27 23:30", "price": 3000, "tickets_left": 3},
    {"id": 695, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-27 23:00", "arr_time": "2025-12-27 04:00", "price": 1500, "tickets_left": 50},
    {"id": 696, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-27 10:00", "arr_time": "2025-12-27 11:30", "price": 800, "tickets_left": 50},
    {"id": 697, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-27 08:00", "arr_time": "2025-12-27 12:00", "price": 2500, "tickets_left": 10},
    {"id": 698, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-27 09:00", "arr_time": "2025-12-27 15:00", "price": 3000, "tickets_left": 10},
    {"id": 699, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-27 12:00", "arr_time": "2025-12-27 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-28 ---
    {"id": 700, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-28 08:00", "arr_time": "2025-12-28 10:15", "price": 1200, "tickets_left": 5},
    {"id": 701, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-28 13:00", "arr_time": "2025-12-28 15:20", "price": 1100, "tickets_left": 5},
    {"id": 702, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-28 18:30", "arr_time": "2025-12-28 20:45", "price": 1000, "tickets_left": 5},
    {"id": 703, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-28 21:00", "arr_time": "2025-12-28 23:15", "price": 950, "tickets_left": 5},
    {"id": 704, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-28 06:00", "arr_time": "2025-12-28 06:40", "price": 500, "tickets_left": 3},
    {"id": 705, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-28 18:00", "arr_time": "2025-12-28 18:40", "price": 500, "tickets_left": 3},
    {"id": 706, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-28 23:00", "arr_time": "2025-12-28 23:30", "price": 3000, "tickets_left": 3},
    {"id": 707, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-28 23:00", "arr_time": "2025-12-28 04:00", "price": 1500, "tickets_left": 50},
    {"id": 708, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-28 10:00", "arr_time": "2025-12-28 11:30", "price": 800, "tickets_left": 50},
    {"id": 709, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-28 08:00", "arr_time": "2025-12-28 12:00", "price": 2500, "tickets_left": 10},
    {"id": 710, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-28 09:00", "arr_time": "2025-12-28 15:00", "price": 3000, "tickets_left": 10},
    {"id": 711, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-28 12:00", "arr_time": "2025-12-28 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-29 ---
    {"id": 712, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-29 08:00", "arr_time": "2025-12-29 10:15", "price": 1200, "tickets_left": 20},
    {"id": 713, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-29 13:00", "arr_time": "2025-12-29 15:20", "price": 1100, "tickets_left": 20},
    {"id": 714, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-29 18:30", "arr_time": "2025-12-29 20:45", "price": 1000, "tickets_left": 20},
    {"id": 715, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-29 21:00", "arr_time": "2025-12-29 23:15", "price": 950, "tickets_left": 20},
    {"id": 716, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-29 06:00", "arr_time": "2025-12-29 06:40", "price": 500, "tickets_left": 3},
    {"id": 717, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-29 18:00", "arr_time": "2025-12-29 18:40", "price": 500, "tickets_left": 3},
    {"id": 718, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-29 23:00", "arr_time": "2025-12-29 23:30", "price": 3000, "tickets_left": 3},
    {"id": 719, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-29 23:00", "arr_time": "2025-12-29 04:00", "price": 1500, "tickets_left": 50},
    {"id": 720, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-29 10:00", "arr_time": "2025-12-29 11:30", "price": 800, "tickets_left": 50},
    {"id": 721, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-29 08:00", "arr_time": "2025-12-29 12:00", "price": 2500, "tickets_left": 10},
    {"id": 722, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-29 09:00", "arr_time": "2025-12-29 15:00", "price": 3000, "tickets_left": 10},
    {"id": 723, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-29 12:00", "arr_time": "2025-12-29 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-30 ---
    {"id": 724, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-30 08:00", "arr_time": "2025-12-30 10:15", "price": 1200, "tickets_left": 20},
    {"id": 725, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-30 13:00", "arr_time": "2025-12-30 15:20", "price": 1100, "tickets_left": 20},
    {"id": 726, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-30 18:30", "arr_time": "2025-12-30 20:45", "price": 1000, "tickets_left": 20},
    {"id": 727, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-30 21:00", "arr_time": "2025-12-30 23:15", "price": 950, "tickets_left": 20},
    {"id": 728, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-30 06:00", "arr_time": "2025-12-30 06:40", "price": 500, "tickets_left": 3},
    {"id": 729, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-30 18:00", "arr_time": "2025-12-30 18:40", "price": 500, "tickets_left": 3},
    {"id": 730, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-30 23:00", "arr_time": "2025-12-30 23:30", "price": 3000, "tickets_left": 3},
    {"id": 731, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-30 23:00", "arr_time": "2025-12-30 04:00", "price": 1500, "tickets_left": 50},
    {"id": 732, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-30 10:00", "arr_time": "2025-12-30 11:30", "price": 800, "tickets_left": 50},
    {"id": 733, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-30 08:00", "arr_time": "2025-12-30 12:00", "price": 2500, "tickets_left": 10},
    {"id": 734, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-30 09:00", "arr_time": "2025-12-30 15:00", "price": 3000, "tickets_left": 10},
    {"id": 735, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-30 12:00", "arr_time": "2025-12-30 16:00", "price": 1200, "tickets_left": 10},
    # --- 2025-12-31 ---
    {"id": 736, "flight_no": "CA1501", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-31 08:00", "arr_time": "2025-12-31 10:15", "price": 1800, "tickets_left": 20},
    {"id": 737, "flight_no": "MU5109", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-31 13:00", "arr_time": "2025-12-31 15:20", "price": 1650, "tickets_left": 20},
    {"id": 738, "flight_no": "HU7605", "src_iata": "PEK", "dest_iata": "SHA", "dep_time": "2025-12-31 18:30", "arr_time": "2025-12-31 20:45", "price": 1500, "tickets_left": 20},
    {"id": 739, "flight_no": "CZ3908", "src_iata": "SHA", "dest_iata": "PEK", "dep_time": "2025-12-31 21:00", "arr_time": "2025-12-31 23:15", "price": 1425, "tickets_left": 20},
    {"id": 740, "flight_no": "GTI-Alpha", "src_iata": "HVK", "dest_iata": "BKS", "dep_time": "2025-12-31 06:00", "arr_time": "2025-12-31 06:40", "price": 500, "tickets_left": 3},
    {"id": 741, "flight_no": "GTI-Beta", "src_iata": "BKS", "dest_iata": "HVK", "dep_time": "2025-12-31 18:00", "arr_time": "2025-12-31 18:40", "price": 500, "tickets_left": 3},
    {"id": 742, "flight_no": "MANDEL-X", "src_iata": "BKS", "dest_iata": "ZDM", "dep_time": "2025-12-31 23:00", "arr_time": "2025-12-31 23:30", "price": 3000, "tickets_left": 3},
    {"id": 743, "flight_no": "PL-001", "src_iata": "LGM", "dest_iata": "LND", "dep_time": "2025-12-31 23:00", "arr_time": "2025-12-31 04:00", "price": 1500, "tickets_left": 50},
    {"id": 744, "flight_no": "PL-520", "src_iata": "LGM", "dest_iata": "SHS", "dep_time": "2025-12-31 10:00", "arr_time": "2025-12-31 11:30", "price": 800, "tickets_left": 50},
    {"id": 745, "flight_no": "KRL-BOSS", "src_iata": "KJR", "dest_iata": "LGM", "dep_time": "2025-12-31 08:00", "arr_time": "2025-12-31 12:00", "price": 2500, "tickets_left": 10},
    {"id": 746, "flight_no": "RL-Sci", "src_iata": "NCX", "dest_iata": "YUM", "dep_time": "2025-12-31 09:00", "arr_time": "2025-12-31 15:00", "price": 3000, "tickets_left": 10},
    {"id": 747, "flight_no": "LTR-BOOM", "src_iata": "LTR", "dest_iata": "LGM", "dep_time": "2025-12-31 12:00", "arr_time": "2025-12-31 16:00", "price": 1200, "tickets_left": 10},
    {"id": 748, "flight_no": "NC-2077", "src_iata": "NCX", "dest_iata": "LSX", "dep_time": "2025-12-31 20:00", "arr_time": "2025-12-31 21:30", "price": 2000, "tickets_left": 0},
    {"id": 749, "flight_no": "SR-1001", "src_iata": "XZL", "dest_iata": "PNY", "dep_time": "2025-12-31 10:00", "arr_time": "2025-12-31 18:00", "price": 9999, "tickets_left": 0},


]

# 4. 模拟数据库：订单表
orders_db = []

# ================= 核心逻辑 =================

def send_packet(conn, json_data):
    """打包并发送：4字节长度头 + JSON body"""
    body = json.dumps(json_data).encode('utf-8')
    header = struct.pack('>I', len(body))
    conn.sendall(header + body)
    print(f"   📤 [Resp] {json_data.get('type')}")

def handle_client(conn, addr):
    print(f"✅ 新连接: {addr}")

    try:
        while True:
            header = conn.recv(4)
            if not header: break
            body_len = struct.unpack('>I', header)[0]
            
            body = b""
            while len(body) < body_len:
                packet = conn.recv(body_len - len(body))
                if not packet: break
                body += packet
            if not body: break

            req = json.loads(body.decode('utf-8'))
            req_type = req.get('type')
            print(f"📩 [Recv] {req_type} -> {req}")
            
            response = {}

            # --- A. 注册 ---
            if req_type == "register":
                new_user = req.get('username')
                new_pass = req.get('password')
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
                        "user_id": found['id'], # 客户端已经适配了数字和字符串，这里传数字没问题
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
                search_date = req.get('date') 
                
                # 1. 找出该城市对应的所有 IATA Code
                src_iatas = [a['iata_code'] for a in airports_db if a['city_name'] == src_city]
                dest_iatas = [a['iata_code'] for a in airports_db if a['city_name'] == dest_city]
                
                # 2. 筛选航班
                matched_flights = []
                for f in flights_db:
                    flight_date = f['dep_time'][:10] 
                    # 【修正】字段名匹配 src_iata 和 dest_iata
                    if (f['src_iata'] in src_iatas and 
                        f['dest_iata'] in dest_iatas and 
                        flight_date == search_date):
                        matched_flights.append(f)
                
                response = {"type": "search_flights_res", "data": matched_flights}

            # --- E. 购买机票 ---
            elif req_type == "buy_ticket":
                f_id = req.get('flight_id')
                u_id = req.get('user_id')
                
                target_flight = next((f for f in flights_db if f['id'] == f_id), None)
                
                res_type = "buy_ticket_res"

                if target_flight:
                    if target_flight['tickets_left'] > 0:
                        target_flight['tickets_left'] -= 1
                        orders_db.append({
                            "order_id": len(orders_db) + 9000,
                            "user_id": u_id,
                            "flight_id": f_id,
                            "order_time": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        response = {"type": res_type, "result": True, "message": "购票成功！"}
                    else:
                        response = {"type": res_type, "result": False, "message": "已售罄"}
                else:
                    response = {"type": res_type, "result": False, "message": "航班不存在"}

            # --- G. 修改密码 ---
            elif req_type == "change_password":
                u_id = req.get('user_id')
                old_pass = req.get('old_pass')
                new_pass = req.get('new_pass')

                target_user = None
                for user in users_db:
                    if user['id'] == u_id and user['password'] == old_pass:
                        target_user = user
                        break
                
                if target_user:
                    target_user['password'] = new_pass
                    print(f"🔑 用户 {target_user['username']} 密码已更新")
                    response = {"type": "change_password_res", "result": True, "message": "密码修改成功！"}
                else:
                    response = {"type": "change_password_res", "result": False, "message": "旧密码错误"}
            
            else:
                print(f"⚠️ 未知类型: {req_type}")
                continue

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