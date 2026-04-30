import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia
import com.scythestudio.scodes 1.0

ColumnLayout {
    Label {
        id: label
        visible: label.text !== ""
    }

    Button {
        text: "Scan"

        Layout.alignment: Qt.AlignCenter

        onClicked: {
            if (cameraPermission.status === Qt.Granted) {
                dialog.open();
            } else if (cameraPermission.status === Qt.Denied) {
                label.text = "Camera access is disabled";
            } else {
                cameraPermission.request();
            }
        }
    }

    CameraPermission {
        id: cameraPermission

        onStatusChanged: {
            if (cameraPermission.status === Qt.Granted) {
                dialog.open();
            } else if (cameraPermission.status === Qt.Denied) {
                label.text = "Camera access is disabled";
            }
        }
    }

    Dialog {
        id: dialog
        modal: true

        width: 250
        height: 250

        anchors.centerIn: parent

        VideoOutput {
            id: videoOutput

            width: 200
            height: 200

            fillMode: VideoOutput.PreserveAspectCrop
            anchors.centerIn: parent
        }
    }

    Loader {
        active: dialog.opened

        sourceComponent: SBarcodeScanner {
            forwardVideoSink: videoOutput.videoSink

            onCapturedChanged: function (captured) {
                label.text = captured;
                dialog.close();
            }
        }
    }
}
