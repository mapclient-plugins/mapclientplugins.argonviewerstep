import os
import webbrowser

from PySide6 import QtCore, QtWidgets

from cmlibs.argon.utilities import is_argon_file

from mapclientplugins.argonviewerstep.ui_configuredialog import Ui_ConfigureDialog

INVALID_STYLE_SHEET = 'background-color: rgba(239, 0, 0, 50)'
DEFAULT_STYLE_SHEET = ''


class ConfigureDialog(QtWidgets.QDialog):
    """
    Configure dialog to present the user with the options to configure this step.
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self._ui = Ui_ConfigureDialog()
        self._ui.setupUi(self)

        # Keep track of the previous identifier so that we can track changes
        # and know how many occurrences of the current identifier there should
        # be.
        self._previousIdentifier = ''
        # Set a placeholder for a callable that will get set from the step.
        # We will use this method to decide whether the identifier is unique.
        self.identifierOccursCount = None
        self._documents_dir = None
        self._original_documents = []

        self.setWhatsThis(
            '<html>Please read the documentation available \n<a href="https://abi-mapping-tools.readthedocs.io/en/latest/mapclientplugins.argonviewerstep/docs/index.html">here'
            '</a> for further details.</html>')

        self._make_connections()

    def event(self, e):
        if e.type() == QtCore.QEvent.Type.WhatsThisClicked:
            webbrowser.open(e.href())
        return super().event(e)

    def _make_connections(self):
        self._ui.lineEditIdentifier.textChanged.connect(self.validate)
        line_edit = self._ui.comboBoxVisualisationDocuments.lineEdit()
        line_edit.editingFinished.connect(self._document_name_changed)

    def _document_name_changed(self):
        index = self._ui.comboBoxVisualisationDocuments.currentIndex()
        new_text = self._ui.comboBoxVisualisationDocuments.currentText()
        self._ui.comboBoxVisualisationDocuments.setItemText(index, new_text)

    def _do_document_name_change(self, old_name, new_name):
        if not os.path.isfile(os.path.join(self._documents_dir, new_name)):
            os.replace(os.path.join(self._documents_dir, old_name), os.path.join(self._documents_dir, new_name))

    def accept(self):
        """
        Override the accept method so that we can confirm saving an
        invalid configuration.
        """
        result = QtWidgets.QMessageBox.StandardButton.Yes
        if not self.validate():
            result = QtWidgets.QMessageBox.warning(
                self, 'Invalid Configuration',
                'This configuration is invalid.  Unpredictable behaviour may result if you choose \'Yes\', are you sure you want to save this configuration?)',
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No)

        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            QtWidgets.QDialog.accept(self)

            items_text = []
            for r in range(1, self._ui.comboBoxVisualisationDocuments.count()):
                items_text.append(self._ui.comboBoxVisualisationDocuments.itemText(r))

            for old_text, new_text in zip(self._original_documents, items_text):
                print(old_text, new_text)
                if old_text != new_text:
                    self._do_document_name_change(old_text, new_text)

    def validate(self):
        """
        Validate the configuration dialog fields.  For any field that is not valid
        set the style sheet to the INVALID_STYLE_SHEET.  Return the outcome of the
        overall validity of the configuration.
        """
        # Determine if the current identifier is unique throughout the workflow
        # The identifierOccursCount method is part of the interface to the workflow framework.
        value = self.identifierOccursCount(self._ui.lineEditIdentifier.text())
        valid = (value == 0) or (value == 1 and self._previousIdentifier == self._ui.lineEditIdentifier.text())
        self._ui.lineEditIdentifier.setStyleSheet(DEFAULT_STYLE_SHEET if valid else INVALID_STYLE_SHEET)

        return valid

    def getConfig(self):
        """
        Get the current value of the configuration from the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = self._ui.lineEditIdentifier.text()
        return {
            'identifier': self._ui.lineEditIdentifier.text(),
            'auto-load-visualisation-doc': self._ui.checkBoxAutoLoadVisualisationDocument.isChecked(),
            'visualisation-doc': self._ui.comboBoxVisualisationDocuments.currentText()
        }

    def setConfig(self, config):
        """
        Set the current value of the configuration for the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = config['identifier']
        self._ui.lineEditIdentifier.setText(config['identifier'])
        self._ui.checkBoxAutoLoadVisualisationDocument.setChecked(True if config['auto-load-visualisation-doc'] else False)
        index = self._ui.comboBoxVisualisationDocuments.findText(config['visualisation-doc'])
        if index >= 0:
            self._ui.comboBoxVisualisationDocuments.blockSignals(True)
            self._ui.comboBoxVisualisationDocuments.setCurrentIndex(index)
            self._ui.comboBoxVisualisationDocuments.blockSignals(False)

    def setVisualisationDocumentsDir(self, documents_dir):
        self._documents_dir = documents_dir
        documents = [doc for doc in os.listdir(documents_dir) if is_argon_file(os.path.join(documents_dir, doc))]
        self._ui.comboBoxVisualisationDocuments.blockSignals(True)
        self._original_documents = documents[:]
        self._ui.comboBoxVisualisationDocuments.addItems(['', *documents])
        self._ui.comboBoxVisualisationDocuments.blockSignals(False)
