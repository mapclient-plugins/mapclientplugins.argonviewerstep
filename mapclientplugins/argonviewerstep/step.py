"""
MAP Client Plugin Step
"""
import json
import os.path

from PySide6 import QtGui, QtWidgets, QtCore

from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint
from mapclient.settings.general import get_configuration_file

from mapclientplugins.argonviewerstep.configuredialog import ConfigureDialog
from mapclientplugins.argonviewerstep.view.argonviewerwidget import ArgonViewerWidget
from mapclientplugins.argonviewerstep.model.argonviewermodel import ArgonViewerModel


class ArgonViewerStep(WorkflowStepMountPoint):

    def __init__(self, location):
        super(ArgonViewerStep, self).__init__('Argon Viewer', location)
        self._configured = False  # A step cannot be executed until it has been configured.
        self._category = 'Model Viewer'
        # Add any other initialisation code here:
        self._icon = QtGui.QImage(':/argonviewerstep/images/model-viewer.png')
        # Ports:
        self.addPort([('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'),
                      ('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#uses-list-of',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location')
                      ])
        # Ports:
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                      'https://cmlibs.org/1.0/rdf-schema#ArgonDocument'))
        # Config:
        self._config = {
            'identifier': '',
            'auto-load-visualisation-doc': True,
            'visualisation-doc': '',
        }

        # Port data:
        self._file_locations = None  # file_location
        self._model = None
        self._view = None

    def _setup_model(self):
        self._model = ArgonViewerModel(self._config['visualisation-doc'])
        self._model.setPreviousDocumentsDirectory(self._previous_documents_directory())

    def _update_visualisation_doc(self, visualisation_doc):
        self._config['visualisation-doc'] = visualisation_doc
        with open(get_configuration_file(self._location, self._config['identifier']), 'w') as f:
            f.write(self.serialize())

    def execute(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self._setup_model()
            self._view = ArgonViewerWidget(self._model)
            self._view.set_location(self._location)
            self._view.load(self._file_locations, self._config['auto-load-visualisation-doc'])
            self._view.registerUpdateVisualisationDoc(self._update_visualisation_doc)
            self._view.registerDoneExecution(self._doneExecution)
            self._setCurrentWidget(self._view)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def _previous_documents_directory(self):
        previous_documents_directory = os.path.join(self._location, self._config["identifier"] + "-previous-docs")
        if not os.path.isdir(previous_documents_directory):
            os.mkdir(previous_documents_directory)

        return previous_documents_directory

    def setPortData(self, index, dataIn):
        """
        Add your code here that will set the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        uses port for this step then the index can be ignored.

        :param index: Index of the port to return.
        :param dataIn: The data to set for the port at the given index.
        """
        if not isinstance(dataIn, list):
            dataIn = [dataIn]

        self._file_locations = dataIn  # file_location

    def getPortData(self, index):
        """
        Add your code here that will return the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        provides port for this step then the index can be ignored.

        :param index: Index of the port to return.
        """
        return self._model.getDocument()

    def configure(self):
        """
        This function will be called when the configure icon on the step is
        clicked.  It is appropriate to display a configuration dialog at this
        time.  If the conditions for the configuration of this step are complete
        then set:
            self._configured = True
        """
        dlg = ConfigureDialog(self._main_window)
        dlg.identifierOccursCount = self._identifierOccursCount
        dlg.setVisualisationDocumentsDir(self._previous_documents_directory())
        dlg.setConfig(self._config)
        dlg.validate()
        dlg.setModal(True)

        if dlg.exec_():
            self._config = dlg.getConfig()

        self._configured = dlg.validate()
        self._configuredObserver()

    def getIdentifier(self):
        """
        The identifier is a string that must be unique within a workflow.
        """
        return self._config['identifier']

    def setIdentifier(self, identifier):
        """
        The framework will set the identifier for this step when it is loaded.
        """
        self._config['identifier'] = identifier

    def serialize(self):
        """
        Add code to serialize this step to string.  This method should
        implement the opposite of 'deserialize'.
        """
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def deserialize(self, string):
        """
        Add code to deserialize this step from string.  This method should
        implement the opposite of 'serialize'.

        :param string: JSON representation of the configuration in a string.
        """
        self._config.update(json.loads(string))
        self._setup_model()

        d = ConfigureDialog()
        d.identifierOccursCount = self._identifierOccursCount
        d.setConfig(self._config)
        self._configured = d.validate()

    def getAdditionalConfigFiles(self):
        if self._model is None:
            self._setup_model()

        return [self._model.getCurrentDocumentLocation()]
