#include "FlightItem.h"
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QStyleOption>
#include <QPainter>

FlightItem::FlightItem(const FlightInfo &flight, 
                       const QString &srcCity, 
                       const QString &destCity, 
                       QWidget *parent)
    : QWidget(parent)
{
    m_flightId = flight.id;
    m_price = flight.price;
    int tickets = flight.ticketsLeft;

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    this->setStyleSheet("FlightItem { border: 1px solid #ccc; background: white; border-radius: 8px; }");
    mainLayout->setContentsMargins(15, 15, 15, 15); // 给卡片内部留点呼吸空间
    mainLayout->setSpacing(10); // 上下两层的间距

    //  上半部分水平排列
    QWidget *topWidget = new QWidget();
    // 去掉 topWidget 的背景色和边框，只让最外层显示边框
    topWidget->setStyleSheet("border: none; background: transparent;"); 
    QHBoxLayout *topLayout = new QHBoxLayout(topWidget);
    topLayout->setContentsMargins(0, 0, 0, 0); // 内部无边距

    // 左侧块：时间与日期
    QVBoxLayout *topLeftLayout = new QVBoxLayout();
    
    QString timeStr = QString("%1 - %2")
                          .arg(flight.depTime.toString("HH:mm"), 
                               flight.arrTime.toString("HH:mm"));
    QString dateStr = QString("%1 - %2")
                          .arg(flight.depTime.toString("yyyy-MM-dd"), 
                               flight.arrTime.toString("yyyy-MM-dd"));
    QLabel *lblTime = new QLabel(timeStr);
    lblTime->setStyleSheet("font-size: 22px; font-weight: bold; color: #333;");
    
    QLabel *lblDate = new QLabel(dateStr);
    lblDate->setStyleSheet("font-size: 13px; color: #888; margin-top: 2px;");

    topLeftLayout->addWidget(lblTime);
    topLeftLayout->addWidget(lblDate);

    // 中间块：价格与余票
    QVBoxLayout *centerLayout = new QVBoxLayout();
    centerLayout->setAlignment(Qt::AlignCenter); // 让价格居中显示

    QLabel *lblPrice = new QLabel(QString("¥%1").arg(m_price));
    lblPrice->setStyleSheet("font-size: 22px; color: #ff5500; font-weight: bold;");
    
    QLabel *lblStock = new QLabel(QString("余票: %1").arg(tickets));
    lblStock->setStyleSheet("font-size: 12px; color: #666;");
    if (tickets < 5 && tickets > 0) lblStock->setStyleSheet("font-size: 12px; color: #ff5500; font-weight: bold;"); // 余票紧张变色
    if (tickets == 0) lblStock->setStyleSheet("font-size: 12px; color: red;");
    
    centerLayout->addWidget(lblPrice);
    centerLayout->addWidget(lblStock);

    // 右侧块：按钮
    QPushButton *btnBuy = new QPushButton("购买");
    btnBuy->setCursor(Qt::PointingHandCursor);
    btnBuy->setFixedSize(80, 35); // 固定按钮大小，防止变形
    btnBuy->setStyleSheet("QPushButton { background-color: #0078d7; color: white; border: none; border-radius: 4px; font-weight: bold; font-size: 14px; }"
                          "QPushButton:hover { background-color: #006cc1; }"
                          "QPushButton:pressed { background-color: #005a9e; }"
                          "QPushButton:disabled { background-color: #ccc; }");
    
    if (tickets <= 0) {
        btnBuy->setText("售罄");
        btnBuy->setEnabled(false);
    } else {
        connect(btnBuy, &QPushButton::clicked, this, [this](){
            emit purchaseClicked(m_flightId, m_price);
        });
    }

    // 组装上半部分
    topLayout->addLayout(topLeftLayout, 1); // 时间占多一点空间
    topLayout->addStretch();                // 加个弹簧，把价格往右推
    topLayout->addLayout(centerLayout);
    topLayout->addSpacing(20);              // 价格和按钮之间留点空
    topLayout->addWidget(btnBuy);

    //  下半部分 航班号与航线
    QString routeStr = QString("航班 %1  |  %2 (%3)  ✈  %4 (%5)")
                           .arg(flight.flightNo, 
                                srcCity, flight.srcIata, 
                                destCity, flight.destIata);
    
    QLabel *lblRoute = new QLabel(routeStr);
    lblRoute->setStyleSheet("color: #666; font-size: 12px; font-family: 'Microsoft YaHei';");
    lblRoute->setWordWrap(true); // 如果实在太长，允许换行

    // 组装
    mainLayout->addWidget(topWidget);
    mainLayout->addWidget(lblRoute); // 航线信息放最下面
}
void FlightItem::paintEvent(QPaintEvent *)
{
    QStyleOption opt;
    opt.initFrom(this);
    QPainter p(this);
    style()->drawPrimitive(QStyle::PE_Widget, &opt, &p, this);
}