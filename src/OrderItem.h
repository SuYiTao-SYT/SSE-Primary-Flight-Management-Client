#ifndef ORDERITEM_H
#define ORDERITEM_H

#include <QWidget>
#include "DataTypes.h"

class OrderItem : public QWidget
{
    Q_OBJECT
public:
    explicit OrderItem(const OrderInfo &info, QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;
};

#endif // ORDERITEM_H