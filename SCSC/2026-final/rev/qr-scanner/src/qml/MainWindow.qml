import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    title: "Qr Scanner"
    width: 500
    height: 500

    property bool scanning: false

    ColumnLayout {
        anchors.centerIn: parent

        Loader {
            id: loader
            Layout.alignment: Qt.AlignCenter

            source: Qt.resolvedUrl("Generator.qml")
        }

        Button {
            text: root.scanning ? "Generate barcode" : "Scan barcode"
            Layout.alignment: Qt.AlignCenter

            onClicked: {
                loader.source = root.scanning ? Qt.resolvedUrl("Generator.qml") : Qt.resolvedUrl("Scanner.qml");
                root.scanning = !root.scanning;
            }
        }
    }
}
