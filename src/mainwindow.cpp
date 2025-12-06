#include "MainWindow.h"
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>
#include "NetworkClient.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setupUi();
    
    NetworkClient::instance().connectToServer("127.0.0.1", 12345);
}

MainWindow::~MainWindow()
{
}

void MainWindow::setupUi()
{
    // 设置窗口标题和大小
    this->setWindowTitle("飞机票购票系统 - 客户端");
    this->resize(800, 600);

    // 创建中心部件
    QWidget *centralWidget = new QWidget(this);
    this->setCentralWidget(centralWidget);

    // 创建主布局
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

    // 临时加个 Label 证明跑起来了
    QLabel *testLabel = new QLabel("系统正在初始化...", this);
    testLabel->setAlignment(Qt::AlignCenter);
    mainLayout->addWidget(testLabel);
}