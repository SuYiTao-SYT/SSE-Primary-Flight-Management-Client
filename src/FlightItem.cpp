#include "FlightItem.h"
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>

FlightItem::FlightItem(const QJsonObject &flight, 
                       const QString &srcCity, 
                       const QString &destCity, 
                       QWidget *parent)
    : QWidget(parent)
{
    m_flightId = flight["id"].toInt();
    m_price = flight["price"].toDouble();
    int tickets = flight["tickets_left"].toInt();

    // 采用水平布局： [时间/机场信息] --- [价格] --- [购买按钮]
    QHBoxLayout *mainLayout = new QHBoxLayout(this);
    
    // 给个边框和背景色，让它看起来像张卡片
    this->setStyleSheet("FlightItem { border: 1px solid #ccc; background: white; border-radius: 5px; }");

    // 左侧：时间与机场
    QVBoxLayout *leftLayout = new QVBoxLayout();
    QString timeStr = QString("%1 - %2").arg(flight["dep_time"].toString(), flight["arr_time"].toString());
    QString routeStr = QString("%1 (%2) -> %3 (%4)")
                           .arg(srcCity, flight["src_iata"].toString(), 
                                destCity, flight["dest_iata"].toString());
    
    QLabel *lblTime = new QLabel(timeStr);
    lblTime->setStyleSheet("font-size: 16px; font-weight: bold; color: #333;");
    
    QLabel *lblRoute = new QLabel(routeStr);
    lblRoute->setStyleSheet("color: #666;");

    leftLayout->addWidget(lblTime);
    leftLayout->addWidget(lblRoute);

    // 中间：价格与余票
    QVBoxLayout *centerLayout = new QVBoxLayout();
    QLabel *lblPrice = new QLabel(QString("¥%1").arg(m_price));
    lblPrice->setStyleSheet("font-size: 18px; color: #ff5500; font-weight: bold;");
    
    QLabel *lblStock = new QLabel(QString("余票: %1").arg(tickets));
    if (tickets == 0) lblStock->setStyleSheet("color: red;");
    
    centerLayout->addWidget(lblPrice);
    centerLayout->addWidget(lblStock);

    // 右侧：按钮
    QPushButton *btnBuy = new QPushButton("购买");
    if (tickets <= 0) {
        btnBuy->setText("售罄");
        btnBuy->setEnabled(false);
    } else {
        connect(btnBuy, &QPushButton::clicked, this, [this](){
            emit purchaseClicked(m_flightId, m_price);
        });
    }

    // 添加到主布局
    mainLayout->addLayout(leftLayout, 1);
    mainLayout->addLayout(centerLayout);
    mainLayout->addWidget(btnBuy);
}