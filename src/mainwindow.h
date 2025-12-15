#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QMap>
#include <QLabel>
#include <QJsonObject>
#include <QStackedWidget>
#include <QLineEdit>
#include <QPushButton>
#include <QScrollArea>
#include "DataTypes.h"
#include <QDate>
#include <QCalendarWidget>

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onDataReceived(const QJsonObject &json);
    void onServerConnected();

    // 按钮槽函数
    void onLoginClicked();
    void onRegisterClicked();
    void onSearchClicked();         // 点击查询按钮
    void onBuyTicket(int flightId); // 点击购买
    
    // 修改密码按钮点击
    void onChangePasswordClicked(); 

    //  城市选择相关
    void onSelectSrcCity();  // 点击“选择出发地”
    void onSelectDestCity(); // 点击“选择目的地”
    void onCitySelected(const QString &cityName); // 在列表里选中了某个城市
    void onIndexLetterClicked(const QString &letter); // 点击右侧索引条

private:
    void setupUi();
    void initLoginPage();      // Page 0
    void initSearchHomePage(); // Page 1: 查询主页
    void initCitySelectPage(); // Page 2: 城市选择页
    void initFlightListPage(); // Page 3: 航班列表页
    void initPersonalCenterPage(); // Page 4: 个人中心页

    // 辅助函数
    void updateDateBar();  
    void doSearchFlights();

    
    // 重新根据 m_airportCache 渲染城市列表
    void renderCityList();

    // 处理密码修改的核心业务逻辑 (校验 + 发送)
    void handlePasswordChange(const QString &oldPass, const QString &newPass, const QString &confirmPass);

    QStackedWidget *m_stackedWidget;

    // 登录页控件
    QLineEdit *m_userEdit;
    QLineEdit *m_passEdit;

    // 查询主页控件
    QPushButton *m_btnSrcCity;  // 显示当前选中的出发地
    QPushButton *m_btnDestCity; // 显示当前选中的目的地
    QPushButton *m_btnDate; 
    QDate m_selectedDate;
    // 城市选择页控件
    QWidget *m_cityListContainer; // 放城市按钮的容器
    QMap<QString, QLabel*> m_letterLabels;
    QScrollArea *m_cityScrollArea; // 首字母跳转

    // 航班列表页控件
    QWidget *m_flightListContainer; 
    QWidget *m_dateBarContainer; 

    // 缓存查询条件
    QString m_lastSrcCity;  
    QString m_lastDestCity;

    // 个人中心页控件
    // 需要保存这个指针，以便在进入个人中心时更新 "当前账号: xxx"
    QLabel *m_lblCenterUser; 


    int m_userId = -1;
    QMap<QString, AirportInfo> m_airportCache;
    
    // 状态标志：true表示正在选出发地，false表示正在选目的地
    bool m_isSelectingSrc = true; 
};

#endif