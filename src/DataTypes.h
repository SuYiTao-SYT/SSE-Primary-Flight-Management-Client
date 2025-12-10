#ifndef DATATYPES_H
#define DATATYPES_H

#include <QString>
#include <QDateTime>

// 机场信息结构体
struct AirportInfo{
    QString iata;
    QString city;
    QString name;
    QString pinyin;
};

struct FlightInfo {
    int id;
    QString flightNo;
    QString srcIata;
    QString destIata;
    QDateTime depTime;
    QDateTime arrTime;
    double price;
    int ticketsLeft;
};

#endif