#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QMap>
#include <QJsonObject>
#include "DataTypes.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    // 处理网络数据的槽函数
    void onDataReceived(const QJsonObject &json);
    
    // 连接成功后自动执行的逻辑
    void onServerConnected();

private:
    void setupUi();

    // 本地机场缓存：IATA->机场详情
    QMap<QString, AirportInfo> m_airportCache;
};

#endif // MAINWINDOW_H