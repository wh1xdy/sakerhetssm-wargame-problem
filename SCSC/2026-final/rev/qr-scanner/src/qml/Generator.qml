import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import com.scythestudio.scodes 1.0

ColumnLayout {
    spacing: 8

    ComboBox {
        id: selectedFormat

        model: ListModel {
            ListElement {
                text: "QR Code"
                value: "QRCode"
            }

            ListElement {
                text: "Data Matrix"
                value: "DataMatrix"
            }

            ListElement {
                text: "UPC-A"
                value: "UPCA"
            }

            ListElement {
                text: "UPC-E"
                value: "UPCE"
            }

            ListElement {
                text: "EAN-8"
                value: "EAN8"
            }

            ListElement {
                text: "EAN-13"
                value: "EAN13"
            }

            ListElement {
                text: "Code 39"
                value: "Code39"
            }

            ListElement {
                text: "Code 93"
                value: "Code93"
            }

            ListElement {
                text: "Code 128"
                value: "Code128"
            }

            ListElement {
                text: "Codabar"
                value: "Codabar"
            }

            ListElement {
                text: "Aztec"
                value: "Aztec"
            }

            ListElement {
                text: "PDF417"
                value: "PDF417"
            }
        }

        textRole: "text"
        valueRole: "value"

        Layout.alignment: Qt.AlignCenter
    }

    TextField {
        id: qrTextField

        placeholderText: "Value"

        Layout.alignment: Qt.AlignCenter
    }

    Label {
        id: errorLabel

        visible: text !== ""

        Layout.alignment: Qt.AlignCenter
    }

    Button {
        text: "Generate"

        Layout.alignment: Qt.AlignCenter

        onClicked: codeGenerator.generate(qrTextField.text)
    }

    SBarcodeGenerator {
        id: codeGenerator

        format: selectedFormat.currentValue

        onGenerationFinished: function (error) {
            if (error === "") {
                errorLabel.text = "";

                popupImage.source = "";
                popupImage.source = "file:///" + codeGenerator.filePath;
                dialog.open();
            } else {
                errorLabel.text = error;
            }
        }
    }

    Dialog {
        id: dialog
        modal: true

        width: 200
        height: 200

        anchors.centerIn: parent

        contentItem: Image {
            id: popupImage
            height: 200
            width: 200

            cache: false
            asynchronous: true
        }
    }
}
