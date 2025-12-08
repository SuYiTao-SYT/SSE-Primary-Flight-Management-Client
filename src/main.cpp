#include <QApplication>
#include <QStyleFactory> // 引入风格工厂
#include <QPalette>      // 引入调色板
#include "MainWindow.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);


    a.setStyle(QStyleFactory::create("Fusion"));

    QPalette lightPalette;
    lightPalette.setColor(QPalette::Window, QColor(240, 240, 240));      // 窗口背景色
    lightPalette.setColor(QPalette::WindowText, Qt::black);              // 窗口文字色
    lightPalette.setColor(QPalette::Base, Qt::white);                    // 输入框/列表背景色
    lightPalette.setColor(QPalette::AlternateBase, QColor(233, 233, 233));
    lightPalette.setColor(QPalette::ToolTipBase, Qt::white);
    lightPalette.setColor(QPalette::ToolTipText, Qt::black);
    lightPalette.setColor(QPalette::Text, Qt::black);                    // 输入框文字色
    lightPalette.setColor(QPalette::Button, QColor(240, 240, 240));      // 按钮背景色
    lightPalette.setColor(QPalette::ButtonText, Qt::black);              // 按钮文字色
    lightPalette.setColor(QPalette::BrightText, Qt::red);
    lightPalette.setColor(QPalette::Link, QColor(42, 130, 218));
    lightPalette.setColor(QPalette::Highlight, QColor(42, 130, 218));    // 选中高亮色
    lightPalette.setColor(QPalette::HighlightedText, Qt::white);         // 选中后的文字色

    a.setPalette(lightPalette);


    MainWindow w;
    w.show();

    return a.exec();
}