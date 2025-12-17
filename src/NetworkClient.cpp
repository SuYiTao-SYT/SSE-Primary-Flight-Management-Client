#include "NetworkClient.h"
#include <QDataStream>
#include <QDebug>

NetworkClient& NetworkClient::instance()
{
    static NetworkClient _instance;
    return _instance;
}

NetworkClient::NetworkClient(QObject *parent) : QObject(parent)
{
    m_socket = new QTcpSocket(this);
    
    // 连接信号槽
    connect(m_socket, &QTcpSocket::readyRead, this, &NetworkClient::onReadyRead);
    connect(m_socket, &QTcpSocket::connected, this, [this](){
        qDebug() << "Connected to server successfully!";
        emit connected(); 
    });
}

NetworkClient::~NetworkClient()
{
    if(m_socket->isOpen())
        m_socket->close();
}

void NetworkClient::connectToServer(const QString &ip, quint16 port)
{
    // 取消之前的连接
    m_socket->abort(); 
    m_socket->connectToHost(ip, port);
}

void NetworkClient::sendRequest(const QJsonObject &json)
{
    QJsonDocument doc(json);
    qDebug().noquote() << "[REQU] Formatted JSON:\n" 
                       << doc.toJson(QJsonDocument::Indented);
    if (m_socket->state() != QAbstractSocket::ConnectedState) {
        qDebug() << "Error: Not connected to server.";
        return;
    }

    // 将JSON转为字节数据
    QByteArray jsonData = QJsonDocument(json).toJson(QJsonDocument::Compact);

    // 构造数据包：[4字节长度] + [数据体]
    QByteArray block;
    QDataStream out(&block, QIODevice::WriteOnly);
    
    // 字节序采用大端模式
    out.setByteOrder(QDataStream::BigEndian); 

    // 写入长度 (quint32 占4字节)
    out<<(quint32)jsonData.size();
    
    // 直接写入原始字节，不经过DataStream
    block.append(jsonData);

    // 发送
    m_socket->write(block);
    m_socket->flush();
}

// 核心：处理粘包/拆包逻辑
void NetworkClient::onReadyRead()
{
    // 将新到达的数据追加到缓冲区
    m_buffer.append(m_socket->readAll());

    while (true) {
        // 包还没到齐，等待下一次 readyRead
        if (m_buffer.size() < 4) {
            return; 
        }

        // 读取头部记录的包体长度
        QDataStream stream(m_buffer);
        stream.setByteOrder(QDataStream::BigEndian);
        quint32 packetSize = 0;
        stream >> packetSize;

        // 完整包大小 = 4字节头 + packetSize
        if (m_buffer.size() < 4 + packetSize) {
            // 数据不够，等待下一次
            return; 
        }

        // 开始提取
        m_buffer.remove(0, 4);
        // 提取数据体
        QByteArray packetData = m_buffer.left(packetSize);
        
        // 从缓冲区移除已提取的数据体
        m_buffer.remove(0, packetSize);

        // 解析 JSON
        QJsonParseError parseError;
        QJsonDocument doc = QJsonDocument::fromJson(packetData, &parseError);
        if (parseError.error == QJsonParseError::NoError && doc.isObject()) {
            emit dataReceived(doc.object());
        } else {
            qDebug() << "JSON Parse Error:" << parseError.errorString();
        }
        
        // 继续 while 循环，处理缓冲区里可能存在的下一个包（粘包情况）
    }
}