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
    initPersonalCenterPage(); // Index 4

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

    //主垂直布局
    QVBoxLayout *layout = new QVBoxLayout(page);
    layout->setContentsMargins(20, 40, 20, 20);

    //创建顶部水平栏
    QHBoxLayout *topBar = new QHBoxLayout();

    QLabel *title = new QLabel("航班查询");
    title->setStyleSheet("font-size: 22px; font-weight: bold;");

    QPushButton *btnMine = new QPushButton("个人中心");
    btnMine->setFixedSize(80, 30);
    btnMine->setStyleSheet("background-color: #0078d7; color: white; border-radius: 5px; font-size: 12px;");

    // 连接跳转信号
    connect(btnMine, &QPushButton::clicked, this, [this](){
        if(m_lblCenterUser) {
            m_lblCenterUser->setText("当前账号: " + m_userEdit->text());
        }
        m_stackedWidget->setCurrentIndex(4);
    });

    topBar->addWidget(title);
    topBar->addStretch();
    topBar->addWidget(btnMine);
    
    layout->addLayout(topBar);
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

// Page 4: 个人中心页
void MainWindow::initPersonalCenterPage()
{
    QWidget *page = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(page);
    layout->setContentsMargins(0, 0, 0, 0);

    //顶部导航栏 (带标题)
    QWidget *navBar = new QWidget();
    navBar->setStyleSheet("background: #f8f8f8; border-bottom: 1px solid #ddd;");
    navBar->setFixedHeight(50);
    QHBoxLayout *navLayout = new QHBoxLayout(navBar);
    
    QLabel *title = new QLabel("个人中心");
    title->setStyleSheet("font-size: 18px; font-weight: bold; color: #333;");
    title->setAlignment(Qt::AlignCenter);
    navLayout->addWidget(title); // 居中标题
    
    layout->addWidget(navBar);

    //内容区域容器
    QWidget *contentWidget = new QWidget();
    QVBoxLayout *contentLayout = new QVBoxLayout(contentWidget);
    contentLayout->setContentsMargins(30, 40, 30, 40);
    contentLayout->setSpacing(20);

    //头像占位符
    QLabel *avatar = new QLabel("👤");
    avatar->setAlignment(Qt::AlignCenter);
    avatar->setStyleSheet("font-size: 60px; background: #eee; border-radius: 40px;");
    avatar->setFixedSize(80, 80);
    
    //用户名显示
    m_lblCenterUser = new QLabel("当前账号: --");
    m_lblCenterUser->setAlignment(Qt::AlignCenter);
    m_lblCenterUser->setStyleSheet("font-size: 18px; color: #555; font-weight: bold;");

    //修改密码按钮
    QPushButton *btnChangePwd = new QPushButton("修改密码");
    btnChangePwd->setFixedHeight(45);
    btnChangePwd->setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 5px; color: #333; font-size: 16px;");

    //修改密码
    connect(btnChangePwd, &QPushButton::clicked, this, [this](){
        //创建对话框
        QDialog dlg(this);
        dlg.setWindowTitle("修改密码");
        dlg.setFixedSize(300, 280);

        //垂直布局
        QVBoxLayout *dlgLayout = new QVBoxLayout(&dlg);
        dlgLayout->setSpacing(10);

        //创建输入控件
        QLineEdit *editOld = new QLineEdit();
        editOld->setPlaceholderText("请输入旧密码");
        editOld->setEchoMode(QLineEdit::Password);

        QLineEdit *editNew = new QLineEdit();
        editNew->setPlaceholderText("请输入新密码");
        editNew->setEchoMode(QLineEdit::Password);

        QLineEdit *editConfirm = new QLineEdit();
        editConfirm->setPlaceholderText("请再次输入新密码");
        editConfirm->setEchoMode(QLineEdit::Password);

        dlgLayout->addWidget(new QLabel("旧密码:"));
        dlgLayout->addWidget(editOld);

        dlgLayout->addWidget(new QLabel("新密码:"));
        dlgLayout->addWidget(editNew);

        dlgLayout->addWidget(new QLabel("确认密码:"));
        dlgLayout->addWidget(editConfirm);

        dlgLayout->addSpacing(10);

        //按钮框
        QDialogButtonBox *buttonBox = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
        dlgLayout->addWidget(buttonBox);

        //连接按钮信号
        connect(buttonBox, &QDialogButtonBox::accepted, &dlg, &QDialog::accept);
        connect(buttonBox, &QDialogButtonBox::rejected, &dlg, &QDialog::reject);

        //执行并处理逻辑
        if (dlg.exec() == QDialog::Accepted) {
            QString oldPass = editOld->text();
            QString newPass = editNew->text();
            QString confirmPass = editConfirm->text();
            handlePasswordChange(oldPass, newPass, confirmPass);
        }
    });

    // 退出/返回按钮
    QPushButton *btnBack = new QPushButton("返回查询");
    btnBack->setFixedHeight(45);
    btnBack->setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc; border-radius: 5px; color: #666; font-size: 16px;");
    
    connect(btnBack, &QPushButton::clicked, this, [this](){
        m_stackedWidget->setCurrentIndex(1);
    });

    // 组装布局
    contentLayout->addWidget(avatar, 0, Qt::AlignHCenter);
    contentLayout->addWidget(m_lblCenterUser);
    contentLayout->addSpacing(30);
    contentLayout->addWidget(btnChangePwd);
    contentLayout->addWidget(btnBack);
    contentLayout->addStretch();

    layout->addWidget(contentWidget);

    m_stackedWidget->addWidget(page);
}


//核心逻辑部分

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
        // 切换到航班列表页
        m_stackedWidget->setCurrentIndex(3);
        
        // 清空容器
        qDeleteAll(m_flightListContainer->findChildren<QWidget*>(Qt::FindDirectChildrenOnly));
        QVBoxLayout *layout = qobject_cast<QVBoxLayout*>(m_flightListContainer->layout());

        QJsonArray flights = json["flights"].toArray();
        if (flights.isEmpty()) {
            QLabel *empty = new QLabel("暂无航班");
            empty->setAlignment(Qt::AlignCenter);
            layout->addWidget(empty);
        } else {
            for (const auto &val : flights) {
                QJsonObject f = val.toObject();
                // IATA 转中文逻辑同前
                QString srcName = f["src_iata"].toString(); // 简化展示，可用 cache 转换
                QString destName = f["dest_iata"].toString();
                if(m_airportCache.contains(srcName)) srcName = m_airportCache[srcName].name;
                if(m_airportCache.contains(destName)) destName = m_airportCache[destName].name;

                FlightItem *item = new FlightItem(f, srcName, destName);
                connect(item, &FlightItem::purchaseClicked, this, &MainWindow::onBuyTicket);
                layout->addWidget(item);
            }
        }
    }
    else if (type == "buy_ticket_res") {
        // 简单的弹窗反馈
        if(json["result"].toBool()) QMessageBox::information(this, "Success", "购票成功!");
        else QMessageBox::warning(this, "Fail", json["message"].toString());
    }
    else if (type == "change_password_res") {
        bool success = json["result"].toBool();
        QString msg = json["message"].toString();

        if (success) {
            QMessageBox::information(this, "成功", msg);
            //修改成功后强制退出登录，或者清空密码框等
        } else {
            QMessageBox::critical(this, "失败", msg);
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

void MainWindow::onChangePasswordClicked()
{
    // 创建对话框
    QDialog dlg(this);
    dlg.setWindowTitle("修改密码");
    dlg.setFixedSize(300, 280); 

    QVBoxLayout *dlgLayout = new QVBoxLayout(&dlg);
    dlgLayout->setSpacing(10); 

    // 创建输入控件
    QLineEdit *editOld = new QLineEdit(); 
    editOld->setPlaceholderText("请输入旧密码");
    editOld->setEchoMode(QLineEdit::Password);
    
    QLineEdit *editNew = new QLineEdit(); 
    editNew->setPlaceholderText("请输入新密码");
    editNew->setEchoMode(QLineEdit::Password);
    
    QLineEdit *editConfirm = new QLineEdit(); 
    editConfirm->setPlaceholderText("请再次输入新密码");
    editConfirm->setEchoMode(QLineEdit::Password);

    // 添加布局
    dlgLayout->addWidget(new QLabel("旧密码:"));
    dlgLayout->addWidget(editOld);
    dlgLayout->addWidget(new QLabel("新密码:"));
    dlgLayout->addWidget(editNew);
    dlgLayout->addWidget(new QLabel("确认密码:"));
    dlgLayout->addWidget(editConfirm);
    dlgLayout->addSpacing(10); 

    // 按钮
    QDialogButtonBox *buttonBox = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
    dlgLayout->addWidget(buttonBox);

    connect(buttonBox, &QDialogButtonBox::accepted, &dlg, &QDialog::accept);
    connect(buttonBox, &QDialogButtonBox::rejected, &dlg, &QDialog::reject);

    // 如果用户点击确定，获取数据并转交给处理函数
    if (dlg.exec() == QDialog::Accepted) {
        QString oldPass = editOld->text();
        QString newPass = editNew->text();
        QString confirmPass = editConfirm->text();

        // 调用业务逻辑函数
        handlePasswordChange(oldPass, newPass, confirmPass);
    }
}

void MainWindow::handlePasswordChange(const QString &oldPass, const QString &newPass, const QString &confirmPass)
{
    //前端校验
    if (oldPass.isEmpty() || newPass.isEmpty()) {
        QMessageBox::warning(this, "提示", "密码不能为空");
        return;
    }

    if (newPass != confirmPass) {
        QMessageBox::warning(this, "错误", "两次输入的新密码不一致");
        return;
    }

    if (oldPass == newPass) {
        QMessageBox::warning(this, "提示", "新密码不能与旧密码相同");
        return;
    }

    //发送网络请求
    QJsonObject req;
    req["type"] = "change_password";
    req["user_id"] = m_userId;
    req["old_pass"] = oldPass;
    req["new_pass"] = newPass;

    NetworkClient::instance().sendRequest(req);
}
