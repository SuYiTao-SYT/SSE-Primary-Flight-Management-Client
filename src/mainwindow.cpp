#include "MainWindow.h"
#include "NetworkClient.h"
#include "FlightItem.h"
#include <QLabel>
#include <QVBoxLayout>
#include <QPushButton>
#include <QMessageBox>
#include <QScrollArea>
#include <QDebug>
#include <QJsonArray>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setupUi();

    // 绑定接收数据的信号
    connect(&NetworkClient::instance(), &NetworkClient::dataReceived, 
            this, &MainWindow::onDataReceived);

    // 绑定连接成功的信号
    connect(&NetworkClient::instance(), &NetworkClient::connected, 
            this, &MainWindow::onServerConnected);
    
    // 开始连接
    NetworkClient::instance().connectToServer("127.0.0.1", 34206);
}

MainWindow::~MainWindow()
{
}


void MainWindow::setupUi()
{
    this->setWindowTitle("飞机票购票系统");
    this->resize(400, 300); // 登录窗口可以小一点

    // 创建堆栈窗口作为中心部件
    m_stackedWidget = new QStackedWidget(this);
    this->setCentralWidget(m_stackedWidget);

    // 初始化两个页面
    initLoginPage();
    initMainPage();

    m_stackedWidget->setCurrentIndex(0);
}

void MainWindow::initLoginPage()
{
    QWidget *loginPage = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(loginPage);
    layout->setContentsMargins(50, 50, 50, 50); // 设置边距

    QLabel *title = new QLabel("欢迎使用购票系统");
    title->setAlignment(Qt::AlignCenter);
    QFont font = title->font();
    font.setPointSize(16);
    title->setFont(font);

    m_userEdit = new QLineEdit();
    m_userEdit->setPlaceholderText("请输入用户名");

    m_passEdit = new QLineEdit();
    m_passEdit->setPlaceholderText("请输入密码");
    m_passEdit->setEchoMode(QLineEdit::Password); // 密码模式

    QPushButton *btnLogin = new QPushButton("登 录");
    QPushButton *btnReg = new QPushButton("注 册");

    // 布局添加控件
    layout->addWidget(title);
    layout->addSpacing(20);
    layout->addWidget(m_userEdit);
    layout->addWidget(m_passEdit);
    layout->addSpacing(20);
    layout->addWidget(btnLogin);
    layout->addWidget(btnReg);
    layout->addStretch(); // 底部弹簧，把控件顶上去

    // 绑定按钮事件
    connect(btnLogin, &QPushButton::clicked, this, &MainWindow::onLoginClicked);
    connect(btnReg, &QPushButton::clicked, this, &MainWindow::onRegisterClicked);

    // 将页面加入堆栈
    m_stackedWidget->addWidget(loginPage);
}



void MainWindow::initMainPage()
{
    QWidget *mainPage = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(mainPage);

    // 顶部查询栏
    QHBoxLayout *searchLayout = new QHBoxLayout();
    
    m_srcCityEdit = new QLineEdit();
    m_srcCityEdit->setPlaceholderText("出发城市 (如: 北京)");
    
    m_destCityEdit = new QLineEdit();
    m_destCityEdit->setPlaceholderText("到达城市 (如: 上海)");
    
    QPushButton *btnSearch = new QPushButton("查询航班");
    connect(btnSearch, &QPushButton::clicked, this, &MainWindow::onSearchClicked);

    searchLayout->addWidget(new QLabel("从:"));
    searchLayout->addWidget(m_srcCityEdit);
    searchLayout->addWidget(new QLabel("到:"));
    searchLayout->addWidget(m_destCityEdit);
    searchLayout->addWidget(btnSearch);

    // 滚动列表区域
    QScrollArea *scrollArea = new QScrollArea();
    scrollArea->setWidgetResizable(true); // 让内部控件随窗口调整大小

    // 创建一个 Widget 作为容器，用来垂直排列所有航班卡片
    m_flightListContainer = new QWidget(); 
    QVBoxLayout *listLayout = new QVBoxLayout(m_flightListContainer);
    listLayout->setAlignment(Qt::AlignTop); // 让条目靠上对齐，不要分散
    
    scrollArea->setWidget(m_flightListContainer);

    // 组装
    layout->addLayout(searchLayout);
    layout->addWidget(scrollArea);

    m_stackedWidget->addWidget(mainPage);
}


// 点击登录
void MainWindow::onLoginClicked()
{
    QString user = m_userEdit->text().trimmed();
    QString pass = m_passEdit->text().trimmed();

    if (user.isEmpty() || pass.isEmpty()) {
        QMessageBox::warning(this, "提示", "用户名或密码不能为空");
        return;
    }

    QJsonObject json;
    json["type"] = "login";
    json["username"] = user;
    json["password"] = pass;
    
    NetworkClient::instance().sendRequest(json);
}

// 点击注册
void MainWindow::onRegisterClicked()
{
    QString user = m_userEdit->text().trimmed();
    QString pass = m_passEdit->text().trimmed();

    if (user.isEmpty() || pass.isEmpty()) {
        QMessageBox::warning(this, "提示", "用户名或密码不能为空");
        return;
    }

    QJsonObject json;
    json["type"] = "register";
    json["username"] = user;
    json["password"] = pass;

    NetworkClient::instance().sendRequest(json);
}

void MainWindow::onServerConnected()
{
    // 连接成功后静默获取机场数据
    QJsonObject req;
    req["type"] = "get_airports";
    NetworkClient::instance().sendRequest(req);
}

void MainWindow::onDataReceived(const QJsonObject &json)
{
    QString type = json["type"].toString();

    // 处理机场列表
    if (type == "get_airports_res") {
        QJsonArray arr = json["data"].toArray();
        m_airportCache.clear();
        for (const auto &val : arr) {
            QJsonObject obj = val.toObject();
            AirportInfo info{obj["iata"].toString(), obj["city"].toString(), obj["name"].toString()};
            m_airportCache.insert(info.iata, info);
        }
        qDebug() << "机场数据已更新:" << m_airportCache.size();
    }
    //处理登录结果
    else if (type == "login_res") {
        bool success = json["result"].toBool();
        QString msg = json["message"].toString();

        if (success) {
            m_userId = json["user_id"].toInt();
            m_stackedWidget->setCurrentIndex(1); // 切到主页
            this->resize(800, 600);
            this->setWindowTitle("购票系统 - " + m_userEdit->text());
        } else {
            QMessageBox::critical(this, "登录失败", msg);
        }
    }
    // 处理注册结果
    else if (type == "register_res") {
        bool success = json["result"].toBool();
        QString msg = json["message"].toString();
        
        if (success) {
            QMessageBox::information(this, "成功", "注册成功，请登录");
        } else {
            QMessageBox::warning(this, "注册失败", msg);
        }
    }
    // 处理航班查询结果
    else if (type == "search_flights_res") {
        // 清空列表
        qDeleteAll(m_flightListContainer->findChildren<QWidget*>(Qt::FindDirectChildrenOnly));

        QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(m_flightListContainer->layout());
        QJsonArray flights = json["flights"].toArray();
        
        if (flights.isEmpty()) {
            QMessageBox::information(this, "提示", "未查询到航班");
            return;
        }

        for (const auto &val : flights) {
            QJsonObject f = val.toObject();
            
            // IATA 转中文
            QString srcIata = f["src_iata"].toString();
            QString destIata = f["dest_iata"].toString();
            QString srcName = m_airportCache.contains(srcIata) ? m_airportCache[srcIata].name : srcIata;
            QString destName = m_airportCache.contains(destIata) ? m_airportCache[destIata].name : destIata;

            FlightItem *item = new FlightItem(f, srcName, destName);
            connect(item, &FlightItem::purchaseClicked, this, &MainWindow::onBuyTicket);
            layout->addWidget(item);
        }
    }
    // 处理购票结果
    else if (type == "buy_ticket_res") {
        bool success = json["result"].toBool();
        QString msg = json["message"].toString();
        
        if (success) {
            QMessageBox::information(this, "恭喜", "购票成功！\n请在'我的订单'中查看。");
            onSearchClicked(); // 刷新列表
        } else {
            QMessageBox::warning(this, "失败", "购票失败: " + msg);
        }
    }
}
// 点击查询按钮
void MainWindow::onSearchClicked()
{
    QString src = m_srcCityEdit->text().trimmed();
    QString dest = m_destCityEdit->text().trimmed();

    if (src.isEmpty() || dest.isEmpty()) {
        QMessageBox::warning(this, "提示", "请输入出发地和目的地");
        return;
    }

    // 发送请求
    QJsonObject req;
    req["type"] = "search_flights";
    req["src_city"] = src;
    req["dest_city"] = dest;
    req["date"] = "2023-12-25"; // 暂时写死，后续可以加 DateEdit
    
    NetworkClient::instance().sendRequest(req);
    
    // 清空旧列表
}

// 处理购买请求
void MainWindow::onBuyTicket(int flightId)
{
    QJsonObject req;
    req["type"] = "buy_ticket";
    req["user_id"] = m_userId;
    req["flight_id"] = flightId;
    
    NetworkClient::instance().sendRequest(req);
}
