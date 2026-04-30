cmake_minimum_required(VERSION 4.1)
project(qrScanner)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(QT_NO_PRIVATE_MODULE_WARNING ON)

include(FetchContent)

FetchContent_Declare(
        SCodes
        GIT_REPOSITORY https://github.com/somcosoftware/SCodes.git
        GIT_TAG f20609213875ee9280136598a6f5f5178ef71361
        SOURCE_SUBDIR src
        PATCH_COMMAND git apply ${CMAKE_CURRENT_SOURCE_DIR}/patches/scodes.patch
        UPDATE_DISCONNECTED 1)

FetchContent_MakeAvailable(SCodes)

find_package(Qt6 COMPONENTS Core Quick Gui Multimedia CorePrivate)

if (QT_KNOWN_POLICY_QTP0004)
    qt_policy(SET QTP0004 NEW)
endif ()


qt_add_resources(QRSCANNER_RESOURCES resources.qrc)

qt_add_executable(qrScanner src/main.cpp ${QRSCANNER_RESOURCES})

target_link_libraries(qrScanner PRIVATE Qt::Core Qt::Quick Qt::Gui Qt::Multimedia Qt::CorePrivate SCodes)

set_target_properties(qrScanner PROPERTIES
        QT_ANDROID_APP_NAME "QR Scanner"
        QT_ANDROID_PACKAGE_NAME "org.example.qrScanner"
        QT_ANDROID_MIN_SDK_VERSION 30)

qt_add_qml_module(qrScanner
    VERSION 1.0
    URI QrScanner
    RESOURCE_PREFIX /qt/qml/
    QML_FILES
        qml/MainWindow.qml
        qml/Scanner.qml
        qml/Generator.qml
)

