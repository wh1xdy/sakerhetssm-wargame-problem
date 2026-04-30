#include <QGuiApplication>
#include <QIcon>
#include <QQmlApplicationEngine>
#include <QWindow>

#include "SBarcodeGenerator.h"
#include "SBarcodeScanner.h"

struct wl_surface;

int main(int argc, char *argv[]) {
    QGuiApplication a(argc, argv);

    QIcon::setThemeName("material");

    qmlRegisterType<SBarcodeGenerator>("com.scythestudio.scodes", 1, 0, "SBarcodeGenerator");
    qmlRegisterType<SBarcodeScanner>("com.scythestudio.scodes", 1, 0, "SBarcodeScanner");

    QQmlApplicationEngine engine("QrScanner", "MainWindow");

    return QGuiApplication::exec();
}
