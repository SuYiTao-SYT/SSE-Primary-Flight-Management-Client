#include "MainWindow.h"
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>
#include <QDebug>
#include <QJsonArray>
#include "NetworkClient.h"

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
    this->setWindowTitle("飞机票购票系统 - 客户端");
    this->resize(800, 600);
    QWidget *centralWidget = new QWidget(this);
    this->setCentralWidget(centralWidget);
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

    QLabel *testLabel = new QLabel("正在连接服务器...", this);
    testLabel->setObjectName("statusLabel"); // 设置个名字方便以后查找更新
    testLabel->setAlignment(Qt::AlignCenter);
    mainLayout->addWidget(testLabel);
}

// 连接成功后，立马请求机场列表
void MainWindow::onServerConnected()
{
    qDebug() << "Server connected, requesting airport list...";
    
    // 请求
    QJsonObject req;
    req["type"] = "get_airports";
    NetworkClient::instance().sendRequest(req);
}

//处理所有收到的包
void MainWindow::onDataReceived(const QJsonObject &json)
{
    QString type = json["type"].toString();

    // --- 处理机场列表响应 ---
    if (type == "get_airports_res") {
        QJsonArray arr = json["data"].toArray();
        
        // 清空旧数据
        m_airportCache.clear();

        // 遍历解析
        for (const auto &val : arr) {
            QJsonObject obj = val.toObject();
            AirportInfo info;
            info.iata = obj["iata"].toString();
            info.city = obj["city"].toString();
            info.name = obj["name"].toString();

            // 存入 Map
            m_airportCache.insert(info.iata, info);
        }

        qDebug() << "机场数据加载完毕，共" << m_airportCache.size() << "个机场";

        // 更新界面提示
        QLabel *lbl = this->findChild<QLabel*>("statusLabel");
        if(lbl) lbl->setText("系统初始化完成！\n已加载机场数据: " + QString::number(m_airportCache.size()));
    }
}