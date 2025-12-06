#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QMap>
#include <QJsonObject>
#include <QStackedWidget>
#include <QLineEdit>
#include "DataTypes.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onDataReceived(const QJsonObject &json);
    void onServerConnected();

    // 按钮点击处理槽函数
    void onLoginClicked();
    void onRegisterClicked();

private:
    void setupUi();
    void initLoginPage(); // 初始化登录页
    void initMainPage();  // 初始化主功能页

    QStackedWidget *m_stackedWidget; // 页面管理器

    // 登录页控件
    QLineEdit *m_userEdit;
    QLineEdit *m_passEdit;

    // 运行时数据
    int m_userId = -1; // -1 表示未登录
    QMap<QString, AirportInfo> m_airportCache;
};

#endif // MAINWINDOW_H