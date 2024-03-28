# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configuredialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_ConfigureDialog(object):
    def setupUi(self, ConfigureDialog):
        if not ConfigureDialog.objectName():
            ConfigureDialog.setObjectName(u"ConfigureDialog")
        ConfigureDialog.resize(552, 293)
        self.gridLayout = QGridLayout(ConfigureDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(ConfigureDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.configGroupBox = QGroupBox(ConfigureDialog)
        self.configGroupBox.setObjectName(u"configGroupBox")
        self.formLayout = QFormLayout(self.configGroupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.labelIdentifier = QLabel(self.configGroupBox)
        self.labelIdentifier.setObjectName(u"labelIdentifier")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelIdentifier)

        self.lineEditIdentifier = QLineEdit(self.configGroupBox)
        self.lineEditIdentifier.setObjectName(u"lineEditIdentifier")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lineEditIdentifier)

        self.labelAutoLoadBackupDocument = QLabel(self.configGroupBox)
        self.labelAutoLoadBackupDocument.setObjectName(u"labelAutoLoadBackupDocument")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.labelAutoLoadBackupDocument)

        self.checkBoxAutoLoadVisualisationDocument = QCheckBox(self.configGroupBox)
        self.checkBoxAutoLoadVisualisationDocument.setObjectName(u"checkBoxAutoLoadVisualisationDocument")
        self.checkBoxAutoLoadVisualisationDocument.setChecked(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.checkBoxAutoLoadVisualisationDocument)

        self.comboBoxVisualisationDocuments = QComboBox(self.configGroupBox)
        self.comboBoxVisualisationDocuments.setObjectName(u"comboBoxVisualisationDocuments")
        self.comboBoxVisualisationDocuments.setEditable(True)
        self.comboBoxVisualisationDocuments.setInsertPolicy(QComboBox.InsertAtCurrent)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.comboBoxVisualisationDocuments)

        self.label = QLabel(self.configGroupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label)


        self.gridLayout.addWidget(self.configGroupBox, 0, 0, 1, 1)


        self.retranslateUi(ConfigureDialog)
        self.buttonBox.accepted.connect(ConfigureDialog.accept)
        self.buttonBox.rejected.connect(ConfigureDialog.reject)

        QMetaObject.connectSlotsByName(ConfigureDialog)
    # setupUi

    def retranslateUi(self, ConfigureDialog):
        ConfigureDialog.setWindowTitle(QCoreApplication.translate("ConfigureDialog", u"Configure Argon Viewer", None))
        self.configGroupBox.setTitle("")
        self.labelIdentifier.setText(QCoreApplication.translate("ConfigureDialog", u"Identifier:  ", None))
        self.labelAutoLoadBackupDocument.setText(QCoreApplication.translate("ConfigureDialog", u"Auto load visualisation document:", None))
        self.checkBoxAutoLoadVisualisationDocument.setText("")
        self.comboBoxVisualisationDocuments.setPlaceholderText(QCoreApplication.translate("ConfigureDialog", u"<new document>", None))
        self.label.setText(QCoreApplication.translate("ConfigureDialog", u"Visualisation document:", None))
    # retranslateUi

