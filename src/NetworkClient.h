#ifndef NETWORKCLIENT_H
#define NETWORKCLIENT_H

#include <QObject>
#include <QTcpSocket>
#include <QJsonObject>
#include <QJsonDocument>

class NetworkClient : public QObject
{
    Q_OBJECT
public:
    // 创建实例并连接服务器
    static NetworkClient& instance();
    void connectToServer(const QString &ip, quint16 port);
    void sendRequest(const QJsonObject &json);

signals:
    // 收包指示信号
    void dataReceived(const QJsonObject &jsonObj);
    
    // 连接成功信号
    void connected();
    

private slots:
    void onReadyRead(); // 处理接收数据

private:
    explicit NetworkClient(QObject *parent = nullptr);
    ~NetworkClient();

    QTcpSocket *m_socket;
    QByteArray m_buffer; // 接收缓冲区
};

#endif