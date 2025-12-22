#include "OrderItem.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QStyleOption>
#include <QPainter>
#include <QDateTime>
#include <QFontMetrics>

OrderItem::OrderItem(const OrderInfo &info, QWidget *parent)
    : QWidget(parent)
{
    // 设置卡片整体样式
    this->setFixedHeight(100);
    this->setStyleSheet(
        "OrderItem { "
        "    background-color: white; "
        "    border-radius: 8px; "
        "    border: 1px solid #e0e0e0; "
        "}"
        "OrderItem:hover { "
        "    border: 1px solid #0078d7; "
        "    background-color: #fcfcfc; "
        "}"
        );

    QHBoxLayout *mainLayout = new QHBoxLayout(this);
    mainLayout->setContentsMargins(15, 10, 15, 10);
    mainLayout->setSpacing(5); // 减小间距，防止挤

    // 数据预处理
    QDateTime dt = QDateTime::fromString(info.depTime, "yyyy-MM-dd HH:mm");
    QString dateStr = dt.toString("MM-dd");
    QString timeStr = dt.toString("HH:mm");
    if (!dt.isValid()) {
        dateStr = info.depTime.left(10);
        timeStr = info.depTime.mid(11, 5);
    }

    // 左侧区域：航班号 + 日期
    QWidget *leftWidget = new QWidget();
    leftWidget->setFixedWidth(70); // 设定容器固定宽度
    QVBoxLayout *leftLayout = new QVBoxLayout(leftWidget);
    leftLayout->setContentsMargins(0,0,0,0);

    QLabel *lblFlightNo = new QLabel(info.flightNo);
    lblFlightNo->setStyleSheet("font-size: 15px; font-weight: bold; color: #333; border:none;");

    QLabel *lblDate = new QLabel(dateStr);
    lblDate->setStyleSheet("font-size: 12px; color: #888; border:none;");

    leftLayout->addWidget(lblFlightNo);
    leftLayout->addWidget(lblDate);
    leftLayout->setAlignment(Qt::AlignLeft | Qt::AlignVCenter);


    // 中间区域：城市 + 机场 + 箭头
    QWidget *centerWidget = new QWidget();
    // 中间区域不设固定宽，让它占满剩余空间
    centerWidget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);

    QHBoxLayout *centerLayout = new QHBoxLayout(centerWidget);
    centerLayout->setContentsMargins(0,0,0,0);
    centerLayout->setSpacing(0);

    // 辅助函数：过长文字显示为 "xxx..."
    auto elideText = [this](const QString &text, int width) -> QString {
        QFont font = this->font();
        font.setPixelSize(12); // 参考下面设置的字号
        QFontMetrics metrics(font);
        return metrics.elidedText(text, Qt::ElideRight, width);
    };

    // [左边]：出发地
    QVBoxLayout *srcLayout = new QVBoxLayout();
    QLabel *lblSrcCity = new QLabel(info.srcCity);
    lblSrcCity->setStyleSheet("font-size: 16px; font-weight: bold; color: #333; border:none;");
    lblSrcCity->setAlignment(Qt::AlignCenter);

    // 限制机场名字长度，假设给它 80px 空间，超长自动截断
    QLabel *lblSrcAirport = new QLabel(elideText(info.srcAirport, 85));
    lblSrcAirport->setStyleSheet("font-size: 11px; color: #666; border:none;");
    lblSrcAirport->setAlignment(Qt::AlignCenter);
    // 鼠标放上去显示全名
    lblSrcAirport->setToolTip(info.srcAirport);

    srcLayout->addWidget(lblSrcCity);
    srcLayout->addWidget(lblSrcAirport);
    srcLayout->setAlignment(Qt::AlignVCenter);

    // [中间]：时间 + 箭头
    QVBoxLayout *arrowLayout = new QVBoxLayout();
    QLabel *lblTimeBig = new QLabel(timeStr);
    lblTimeBig->setAlignment(Qt::AlignCenter);
    lblTimeBig->setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d7; border:none;");

    QLabel *lblArrow = new QLabel("──✈──");
    lblArrow->setAlignment(Qt::AlignCenter);
    lblArrow->setStyleSheet("color: #ccc; font-size: 10px; border:none;");

    arrowLayout->addWidget(lblTimeBig);
    arrowLayout->addWidget(lblArrow);
    arrowLayout->setAlignment(Qt::AlignVCenter);

    // [右边]：目的地
    QVBoxLayout *destLayout = new QVBoxLayout();
    QLabel *lblDestCity = new QLabel(info.destCity);
    lblDestCity->setStyleSheet("font-size: 16px; font-weight: bold; color: #333; border:none;");
    lblDestCity->setAlignment(Qt::AlignCenter);

    // 限制机场名字长度
    QLabel *lblDestAirport = new QLabel(elideText(info.destAirport, 85));
    lblDestAirport->setStyleSheet("font-size: 11px; color: #666; border:none;");
    lblDestAirport->setAlignment(Qt::AlignCenter);
    lblDestAirport->setToolTip(info.destAirport);

    destLayout->addWidget(lblDestCity);
    destLayout->addWidget(lblDestAirport);
    destLayout->setAlignment(Qt::AlignVCenter);

    // 组装中间
    centerLayout->addLayout(srcLayout, 3);
    centerLayout->addLayout(arrowLayout, 2);
    centerLayout->addLayout(destLayout, 3);


    // 右侧区域：价格 + 订单号
    QWidget *rightWidget = new QWidget();
    rightWidget->setFixedWidth(70); // 固定右侧宽度，防止价格变动导致卡片抖动
    QVBoxLayout *rightLayout = new QVBoxLayout(rightWidget);
    rightLayout->setContentsMargins(0,0,0,0);

    QLabel *lblPrice = new QLabel(QString("¥%1").arg(info.price));
    lblPrice->setStyleSheet("font-size: 18px; font-weight: bold; color: #ff5500; border:none;");
    lblPrice->setAlignment(Qt::AlignRight);

    QLabel *lblOrderId = new QLabel(QString("NO.%1").arg(info.orderId));
    lblOrderId->setStyleSheet("font-size: 10px; color: #bbb; border:none;");
    lblOrderId->setAlignment(Qt::AlignRight);

    rightLayout->addWidget(lblPrice);
    rightLayout->addWidget(lblOrderId);
    rightLayout->setAlignment(Qt::AlignRight | Qt::AlignVCenter);

    // 组装到主布局
    mainLayout->addWidget(leftWidget);
    mainLayout->addWidget(centerWidget); // 中间部分会自动拉伸
    mainLayout->addWidget(rightWidget);
}

void OrderItem::paintEvent(QPaintEvent *)
{
    QStyleOption opt;
    opt.initFrom(this);
    QPainter p(this);
    style()->drawPrimitive(QStyle::PE_Widget, &opt, &p, this);
}
