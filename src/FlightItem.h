#ifndef FLIGHTITEM_H
#define FLIGHTITEM_H

#include <QWidget>
#include <QJsonObject>

class FlightItem : public QWidget
{
    Q_OBJECT
public:
    // 传入航班数据、出发地中文、目的地中文
    explicit FlightItem(const QJsonObject &flightData, 
                        const QString &srcCity, 
                        const QString &destCity, 
                        QWidget *parent = nullptr);

signals:
    // 点击购买按钮
    void purchaseClicked(int flightId, double price);

private:
    int m_flightId;
    double m_price;
};

#endif // FLIGHTITEM_H