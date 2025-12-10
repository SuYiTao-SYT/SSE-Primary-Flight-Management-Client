#include "MainWindow.h"
#include "NetworkClient.h"
#include "FlightItem.h"
#include <QLabel>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include <QScrollArea>
#include <QMessageBox>
#include <QDebug>
#include <QJsonArray>
#include <QScrollBar>
#include <QGroupBox>
#include <QDateTime>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setupUi();
    connect(&NetworkClient::instance(), &NetworkClient::dataReceived, this, &MainWindow::onDataReceived);
    connect(&NetworkClient::instance(), &NetworkClient::connected, this, &MainWindow::onServerConnected);
    NetworkClient::instance().connectToServer("127.0.0.1", 34206);
}

MainWindow::~MainWindow() {}

void MainWindow::setupUi()
{
    this->setWindowTitle("飞机票购票系统");
    this->resize(450, 700); // 调整为更像手机APP的长宽比

    m_stackedWidget = new QStackedWidget(this);
    this->setCentralWidget(m_stackedWidget);

    // 按顺序初始化页面
    initLoginPage();       // Index 0
    initSearchHomePage();  // Index 1
    initCitySelectPage();  // Index 2
    initFlightListPage();  // Index 3

    m_stackedWidget->setCurrentIndex(0);
}

// Page 0: 登录页
void MainWindow::initLoginPage()
{
    QWidget *page = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(page);
    layout->setContentsMargins(40, 60, 40, 40);

    QLabel *title = new QLabel("✈️ 差旅助手");
    title->setAlignment(Qt::AlignCenter);
    title->setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d7;");

    m_userEdit = new QLineEdit(); m_userEdit->setPlaceholderText("用户名");
    m_passEdit = new QLineEdit(); m_passEdit->setPlaceholderText("密码"); m_passEdit->setEchoMode(QLineEdit::Password);
    
    QPushButton *btnLogin = new QPushButton("登 录");
    btnLogin->setStyleSheet("background-color: #0078d7; color: white; padding: 10px; border-radius: 5px;");
    QPushButton *btnReg = new QPushButton("注 册");

    layout->addWidget(title);
    layout->addSpacing(30);
    layout->addWidget(m_userEdit);
    layout->addWidget(m_passEdit);
    layout->addSpacing(20);
    layout->addWidget(btnLogin);
    layout->addWidget(btnReg);
    layout->addStretch();

    connect(btnLogin, &QPushButton::clicked, this, &MainWindow::onLoginClicked);
    connect(btnReg, &QPushButton::clicked, this, &MainWindow::onRegisterClicked);
    
    m_stackedWidget->addWidget(page);
}

// Page 1: 查询主页 (选择出发/到达)
void MainWindow::initSearchHomePage()
{
    QWidget *page = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(page);
    layout->setContentsMargins(20, 40, 20, 20);

    // 顶部标题
    QLabel *title = new QLabel("航班查询");
    title->setStyleSheet("font-size: 22px; font-weight: bold;");
    layout->addWidget(title);
    layout->addSpacing(30);

    // 选择区域容器
    QGroupBox *box = new QGroupBox();
    box->setStyleSheet("QGroupBox { background: white; border-radius: 10px; border: 1px solid #ddd; }");
    QVBoxLayout *boxLayout = new QVBoxLayout(box);

    // 出发地按钮
    m_btnSrcCity = new QPushButton("北京"); // 默认值
    m_btnSrcCity->setStyleSheet("text-align: left; font-size: 20px; font-weight: bold; padding: 10px; border: none;");
    QLabel *lblSrc = new QLabel("出发城市");
    lblSrc->setStyleSheet("color: #888; font-size: 12px; margin-left: 10px;");
    
    // 目的地按钮
    m_btnDestCity = new QPushButton("上海"); // 默认值
    m_btnDestCity->setStyleSheet("text-align: left; font-size: 20px; font-weight: bold; padding: 10px; border: none;");
    QLabel *lblDest = new QLabel("到达城市");
    lblDest->setStyleSheet("color: #888; font-size: 12px; margin-left: 10px;");

    // 分割线
    QFrame *line = new QFrame();
    line->setFrameShape(QFrame::HLine);
    line->setStyleSheet("color: #eee;");

    boxLayout->addWidget(lblSrc);
    boxLayout->addWidget(m_btnSrcCity);
    boxLayout->addWidget(line);
    boxLayout->addWidget(lblDest);
    boxLayout->addWidget(m_btnDestCity);

    layout->addWidget(box);
    layout->addSpacing(30);

    // 查询按钮
    QPushButton *btnSearch = new QPushButton("查询航班");
    btnSearch->setStyleSheet("background-color: #ffaa00; color: white; font-size: 18px; padding: 12px; border-radius: 8px; font-weight: bold;");
    layout->addWidget(btnSearch);
    layout->addStretch();

    // 逻辑连接
    connect(m_btnSrcCity, &QPushButton::clicked, this, &MainWindow::onSelectSrcCity);
    connect(m_btnDestCity, &QPushButton::clicked, this, &MainWindow::onSelectDestCity);
    connect(btnSearch, &QPushButton::clicked, this, &MainWindow::onSearchClicked);

    m_stackedWidget->addWidget(page);
}

// Page 2: 城市选择页A-Z列表
void MainWindow::initCitySelectPage()
{
    QWidget *page = new QWidget();
    QHBoxLayout *mainLayout = new QHBoxLayout(page); // 水平布局：左边列表，右边索引
    mainLayout->setContentsMargins(0,0,0,0);

    // 左侧：滚动区域
    m_cityScrollArea = new QScrollArea();
    m_cityScrollArea->setWidgetResizable(true);
    m_cityScrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    
    m_cityListContainer = new QWidget();
    QVBoxLayout *listLayout = new QVBoxLayout(m_cityListContainer);
    listLayout->setAlignment(Qt::AlignTop);
    m_cityScrollArea->setWidget(m_cityListContainer);

    // 右侧：A-Z 索引条
    QWidget *indexBar = new QWidget();
    indexBar->setFixedWidth(30);
    indexBar->setStyleSheet("background: #f0f0f0;");
    QVBoxLayout *indexLayout = new QVBoxLayout(indexBar);
    indexLayout->setContentsMargins(0, 5, 0, 5);
    indexLayout->setSpacing(0);

    // 生成 A-Z 按钮
    for(char c = 'A'; c <= 'Z'; c++){
        QString letter = QString(QChar(c));
        QPushButton *btn = new QPushButton(letter);
        btn->setFlat(true);
        btn->setStyleSheet("QPushButton { font-weight: bold; color: #555; border: none; } QPushButton:hover { color: #0078d7; }");
        btn->setFixedHeight(20);
        indexLayout->addWidget(btn);
        
        connect(btn, &QPushButton::clicked, this, [this, letter](){
            onIndexLetterClicked(letter);
        });
    }
    indexLayout->addStretch();

    mainLayout->addWidget(m_cityScrollArea);
    mainLayout->addWidget(indexBar);

    m_stackedWidget->addWidget(page);
}

// Page 3: 航班列表页
void MainWindow::initFlightListPage()
{
    QWidget *page = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(page);

    // 顶部导航栏
    QWidget *navBar = new QWidget();
    navBar->setStyleSheet("background: #f8f8f8; border-bottom: 1px solid #ddd;");
    QHBoxLayout *navLayout = new QHBoxLayout(navBar);
    
    QPushButton *btnBack = new QPushButton("<- 返回");
    btnBack->setStyleSheet("border: none; color: #0078d7; font-weight: bold;");
    connect(btnBack, &QPushButton::clicked, this, [this](){
        m_stackedWidget->setCurrentIndex(1); 
    });
    
    QLabel *title = new QLabel("航班结果");
    title->setAlignment(Qt::AlignCenter);

    navLayout->addWidget(btnBack);
    navLayout->addWidget(title);
    navLayout->addStretch();
    
    QScrollArea *flightScroll = new QScrollArea(); 
    flightScroll->setWidgetResizable(true);
    flightScroll->setStyleSheet("QScrollArea { border: none; background: #f0f2f5; }");
    // 卡片容器
    m_flightListContainer = new QWidget();
    QVBoxLayout *cardLayout = new QVBoxLayout(m_flightListContainer);
    cardLayout->setAlignment(Qt::AlignTop);
    cardLayout->setSpacing(10);
    
    // 使用局部变量
    flightScroll->setWidget(m_flightListContainer);

    layout->addWidget(navBar);
    layout->addWidget(flightScroll); // 添加局部变量

    m_stackedWidget->addWidget(page);
}

// 核心逻辑部分

void MainWindow::onServerConnected()
{
    NetworkClient::instance().sendRequest(QJsonObject{{"type", "get_airports"}});
}

void MainWindow::onSelectSrcCity()
{
    m_isSelectingSrc = true;
    m_stackedWidget->setCurrentIndex(2); // 跳转到城市选择页
}

void MainWindow::onSelectDestCity()
{
    m_isSelectingSrc = false;
    m_stackedWidget->setCurrentIndex(2);
}

// 动态渲染城市列表 (按字母分组)
void MainWindow::renderCityList()
{
    // 清空现有列表
    qDeleteAll(m_cityListContainer->findChildren<QWidget*>(Qt::FindDirectChildrenOnly));
    m_letterLabels.clear();
    
    QVBoxLayout *mainLayout = qobject_cast<QVBoxLayout*>(m_cityListContainer->layout());

    // 数据分组
    QMap<QString, QStringList> groups;
    for (auto it = m_airportCache.begin(); it != m_airportCache.end(); ++it) {
        QString letter = it.value().pinyin.left(1).toUpper(); 
        QString city = it.value().city;
        if (!groups[letter].contains(city)) {
            groups[letter].append(city);
        }
    }

    // 遍历分组
    int columns = 4; // 每行 4 列

    for (auto it = groups.begin(); it != groups.end(); ++it) {
        QString letter = it.key();
        QStringList cities = it.value();

        // 字母标题
        QLabel *header = new QLabel(letter);
        header->setStyleSheet("background: #f5f5f5; color: #888; font-weight: bold; padding: 5px 12px; font-size: 14px;");
        header->setFixedHeight(32);
        mainLayout->addWidget(header);
        
        m_letterLabels.insert(letter, header);

        // 网格容器
        QWidget *gridContainer = new QWidget();
        QGridLayout *gridLayout = new QGridLayout(gridContainer);
        gridLayout->setContentsMargins(15, 10, 15, 10); // 左右留白
        gridLayout->setSpacing(12); // 按钮间距

        // 等宽处理
        for(int c = 0; c < columns; ++c) {
            gridLayout->setColumnStretch(c, 1);
        }

        //添加按钮
        for (int i = 0; i < cities.size(); ++i) {
            QString city = cities[i];
            QPushButton *btnCity = new QPushButton(city);
            
            // 水平方向填充
            btnCity->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
            btnCity->setFixedHeight(40); // 固定高度
            
            // 样式优化：去掉默认边框阴影，用纯平风格
            btnCity->setStyleSheet(
                "QPushButton { "
                "   background: white; border: 1px solid #e0e0e0; border-radius: 6px; "
                "   color: #333; font-size: 15px;"
                "} "
                "QPushButton:pressed { "
                "   background: #e6f7ff; border-color: #1890ff; color: #1890ff; "
                "}"
            );

            connect(btnCity, &QPushButton::clicked, this, [this, city](){
                onCitySelected(city);
            });

            int row = i / columns;
            int col = i % columns;
            gridLayout->addWidget(btnCity, row, col);
        }

        mainLayout->addWidget(gridContainer);
    }
}
void MainWindow::onIndexLetterClicked(const QString &letter)
{
    if (m_letterLabels.contains(letter)) {
        QLabel *target = m_letterLabels[letter];

        if (m_cityScrollArea) {
            m_cityScrollArea->ensureWidgetVisible(target); 
        }
    }
}

void MainWindow::onCitySelected(const QString &cityName)
{
    // 更新主页按钮文字
    if (m_isSelectingSrc) {
        m_btnSrcCity->setText(cityName);
    } else {
        m_btnDestCity->setText(cityName);
    }

    // 返回查询主页
    m_stackedWidget->setCurrentIndex(1);
}

void MainWindow::onSearchClicked()
{
    QString src = m_btnSrcCity->text();
    QString dest = m_btnDestCity->text();

    QJsonObject req;
    req["type"] = "search_flights";
    req["src_city"] = src;
    req["dest_city"] = dest;
    NetworkClient::instance().sendRequest(req);
}

void MainWindow::onBuyTicket(int flightId) {
    // 保持之前的逻辑不变
     QJsonObject req;
    req["type"] = "buy_ticket";
    req["user_id"] = m_userId;
    req["flight_id"] = flightId;
    NetworkClient::instance().sendRequest(req);
}

// 数据处理
void MainWindow::onDataReceived(const QJsonObject &json)
{
    QString type = json["type"].toString();

    if (type == "get_airports_res") {
        QJsonArray arr = json["data"].toArray();
        m_airportCache.clear();
        for (const auto &val : arr) {
            QJsonObject obj = val.toObject();
            AirportInfo info;
            info.iata = obj["iata"].toString();
            info.city = obj["city"].toString();
            info.name = obj["name"].toString();
            info.pinyin = obj["pinyin"].toString(); // 读取拼音
            m_airportCache.insert(info.iata, info);
        }
        // 渲染城市列表
        renderCityList();
    }
    else if (type == "login_res") {
        if (json["result"].toBool()) {
            m_userId = json["user_id"].toInt();
            m_stackedWidget->setCurrentIndex(1); // 登录成功去主页
        } else {
            QMessageBox::warning(this, "Error", json["message"].toString());
        }
    }
    else if (type == "search_flights_res") {
        m_stackedWidget->setCurrentIndex(3);
        
        // 清空 UI
        qDeleteAll(m_flightListContainer->findChildren<QWidget*>(Qt::FindDirectChildrenOnly));
        QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(m_flightListContainer->layout());

        QJsonArray flights = json["flights"].toArray();
        if (flights.isEmpty()) {
            QLabel *empty = new QLabel("暂无航班");
            empty->setAlignment(Qt::AlignCenter);
            layout->addWidget(empty);
            return;
        }

        for (const auto &val : flights) {
            QJsonObject f = val.toObject();
            
            // 解析数据，转存到 Struct 中
            FlightInfo info;
            info.id = f["id"].toInt();
            info.flightNo = f["flight_no"].toString(); // 确保 Python 服务器发了这个字段
            info.srcIata = f["src_iata"].toString();
            info.destIata = f["dest_iata"].toString();
            info.price = f["price"].toDouble();
            info.ticketsLeft = f["tickets_left"].toInt();

            // 格式必须与 Python 发送的 "2023-12-25 08:00" 匹配
            info.depTime = QDateTime::fromString(f["dep_time"].toString(), "yyyy-MM-dd HH:mm");
            info.arrTime = QDateTime::fromString(f["arr_time"].toString(), "yyyy-MM-dd HH:mm");

            // 获取城市中文名用于显示
            QString srcName = m_airportCache.contains(info.srcIata) ? m_airportCache[info.srcIata].name : info.srcIata;
            QString destName = m_airportCache.contains(info.destIata) ? m_airportCache[info.destIata].name : info.destIata;

            // 传入处理好的结构体
            FlightItem *item = new FlightItem(info, srcName, destName);
            connect(item, &FlightItem::purchaseClicked, this, &MainWindow::onBuyTicket);
            layout->addWidget(item);
        }
    }
    else if (type == "buy_ticket_res") {
        bool success = json["result"].toBool();
        QString msg = json["message"].toString();

        if (success) {
            QMessageBox::information(this, "恭喜", "购票成功！");
            onSearchClicked(); 
            
        } else {
            QMessageBox::warning(this, "失败", "购票失败: " + msg);
        }
    }
}

void MainWindow::onLoginClicked() {
    QJsonObject json{{"type", "login"}, {"username", m_userEdit->text()}, {"password", m_passEdit->text()}};
    NetworkClient::instance().sendRequest(json);
}
void MainWindow::onRegisterClicked() {
    QJsonObject json{{"type", "register"}, {"username", m_userEdit->text()}, {"password", m_passEdit->text()}};
    NetworkClient::instance().sendRequest(json);
}