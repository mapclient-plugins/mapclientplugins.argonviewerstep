import json
import os.path
import webbrowser

from PySide6 import QtCore, QtGui, QtWidgets

from cmlibs.argon.argonlogger import ArgonLogger
from cmlibs.argon.utilities import is_argon_file

from cmlibs.widgets.materialeditorwidget import MaterialEditorWidget
from cmlibs.widgets.regioneditorwidget import RegionEditorWidget
from cmlibs.widgets.sceneviewereditorwidget import SceneviewerEditorWidget
from cmlibs.widgets.sceneeditorwidget import SceneEditorWidget
from cmlibs.widgets.spectrumeditorwidget import SpectrumEditorWidget
from cmlibs.widgets.tessellationeditorwidget import TessellationEditorWidget
from cmlibs.widgets.timeeditorwidget import TimeEditorWidget
from cmlibs.widgets.fieldlisteditorwidget import FieldListEditorWidget
from cmlibs.widgets.modelsourceseditorwidget import ModelSourcesEditorWidget, ModelSourcesModel
from cmlibs.widgets.addviewwidget import AddView
from cmlibs.widgets.editabletabbar import EditableTabBar
from cmlibs.widgets.viewwidget import ViewWidget
from cmlibs.widgets.logviewerwidget import LogViewerWidget
from cmlibs.widgets.consoleeditorwidget import ConsoleEditorWidget
from cmlibs.widgets.scenelayoutchooserdialog import SceneLayoutChooserDialog

from mapclientplugins.argonviewerstep.ui.ui_argonviewerwidget import Ui_ArgonViewerWidget


class ArgonViewerWidget(QtWidgets.QMainWindow):

    def __init__(self, model, parent=None):
        super(ArgonViewerWidget, self).__init__(parent)
        self._dock_widgets = []
        self._settings = {}
        self._ui = Ui_ArgonViewerWidget()
        self._ui.setupUi(self)
        self._ui.viewTabWidget.setTabBar(EditableTabBar(self.parentWidget()))

        self._location = None  # The last location/directory used by the application

        self._model = model

        self._toolbar = self._ui.toolBar

        self._makeConnections()
        self._setupEditors()
        self._registerEditors()
        self._setupViews()
        self._addDockWidgets()

        self._callback = None
        self._visualisation_doc_callback = None

    def _onDocumentChanged(self):
        document = self._model.getDocument()
        rootRegion = document.getRootRegion()
        zincRootRegion = rootRegion.getZincRegion()

        # Need to pass new Zinc context to dialogs and widgets using global modules.
        zincContext = document.getZincContext()
        self.dockWidgetContentsSpectrumEditor.setSpectrums(document.getSpectrums())
        self.dockWidgetContentsTessellationEditor.setTessellations(document.getTessellations())
        self.dockWidgetContentsMaterialEditor.setMaterials(document.getMaterials())
        self.dockWidgetContentsTimeEditor.setZincContext(zincContext)
        self.dockWidgetContentsConsoleEditor.setDocument(document)

        model_sources_model = ModelSourcesModel(document, self._model.getSources())
        self.dockWidgetContentsModelSources.setModelSourcesModel(zincRootRegion, model_sources_model)

        # Need to pass new root region to the following.
        self.dockWidgetContentsRegionEditor.setRootRegion(rootRegion)
        self.dockWidgetContentsSceneEditor.setZincRootRegion(zincRootRegion)
        self.dockWidgetContentsSceneviewerEditor.setZincRootRegion(zincRootRegion)
        self.dockWidgetContentsFieldEditor.setRootArgonRegion(rootRegion)
        self.dockWidgetContentsFieldEditor.setTimekeeper(zincContext.getTimekeepermodule().getDefaultTimekeeper())

        self._load_views()

    def setZincContext(self, zincContext):
        raise NotImplementedError()

    def set_settings_file(self, file_name):
        self._settings_file_name = file_name

    def _load_settings(self):
        settings_file = self._settings_file_name
        if os.path.isfile(settings_file):
            with open(settings_file, 'r') as f:
                self._settings.update(json.load(f))

    def _save_settings(self):
        settings_file = self._settings_file_name
        with open(settings_file, 'w') as f:
            json.dump(self._settings, f)

    def set_location(self, location):
        self._location = location

    def load(self, file_locations, auto_load_previous):
        current_document_location = self._model.getCurrentDocumentLocation()

        index = 0
        max_files = len(file_locations)
        while index < max_files and not is_argon_file(file_locations[index]):
            index += 1

        load_success = False
        if index < max_files:
            load_success = self._model.load(file_locations[index])

        have_previous_document = os.path.isfile(current_document_location)
        if not load_success and auto_load_previous and have_previous_document:
            load_success = self._model.load(current_document_location)

        if not load_success:
            self._model.new()

        self._model.setSources(file_locations)
        self._onDocumentChanged()

    def getDependentEditors(self):
        return self._dock_widgets

    def registerDependentEditor(self, editor):
        """
        Add the given editor to the list of dependent editors for
        this view.
        """
        self._dock_widgets.append(editor)

    def _makeConnections(self):
        self._ui.pushButtonDocumentation.clicked.connect(self._documentationButtonClicked)
        self._ui.pushButtonDone.clicked.connect(self._doneButtonClicked)
        self._ui.viewTabWidget.tabCloseRequested.connect(self._viewTabCloseRequested)
        self._ui.viewTabWidget.currentChanged.connect(self._currentViewChanged)
        tab_bar = self._ui.viewTabWidget.tabBar()
        tab_bar.tabTextEdited.connect(self._viewTabTextEdited)

    def _addDockWidgets(self):
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidgetModelSources)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.dockWidgetTimeEditor)
        self.tabifyDockWidget(self.dockWidgetTimeEditor, self.dockWidgetLoggerEditor)
        self.tabifyDockWidget(self.dockWidgetLoggerEditor, self.dockWidgetConsoleEditor)
        self.tabifyDockWidget(self.dockWidgetModelSources, self.dockWidgetTessellationEditor)
        self.tabifyDockWidget(self.dockWidgetTessellationEditor, self.dockWidgetSpectrumEditor)
        self.tabifyDockWidget(self.dockWidgetSpectrumEditor, self.dockWidgetSceneEditor)
        self.tabifyDockWidget(self.dockWidgetSceneEditor, self.dockWidgetSceneviewerEditor)
        self.tabifyDockWidget(self.dockWidgetSceneviewerEditor, self.dockWidgetFieldEditor)
        self.tabifyDockWidget(self.dockWidgetFieldEditor, self.dockWidgetRegionEditor)
        self.tabifyDockWidget(self.dockWidgetRegionEditor, self.dockWidgetMaterialEditor)

    def _setupEditors(self):

        self.dockWidgetMaterialEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetMaterialEditor.setWindowTitle('Material Editor')
        self.dockWidgetMaterialEditor.setObjectName("dockWidgetMaterialEditor")
        self.dockWidgetContentsMaterialEditor = MaterialEditorWidget()
        self.dockWidgetContentsMaterialEditor.setObjectName("dockWidgetContentsMaterialEditor")
        self.dockWidgetMaterialEditor.setWidget(self.dockWidgetContentsMaterialEditor)
        self.dockWidgetMaterialEditor.setHidden(True)

        self.dockWidgetModelSources = QtWidgets.QDockWidget(self)
        self.dockWidgetModelSources.setWindowTitle('Model Sources')
        self.dockWidgetModelSources.setObjectName("dockWidgetModelSources")
        self.dockWidgetContentsModelSources = ModelSourcesEditorWidget()
        self.dockWidgetContentsModelSources.setObjectName("dockWidgetContentsModelSources")
        self.dockWidgetContentsModelSources.setEnableAddingModelSources(False)
        self.dockWidgetModelSources.setWidget(self.dockWidgetContentsModelSources)
        self.dockWidgetModelSources.setHidden(False)

        self.dockWidgetRegionEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetRegionEditor.setWindowTitle('Region Editor')
        self.dockWidgetRegionEditor.setObjectName("dockWidgetRegionEditor")
        self.dockWidgetContentsRegionEditor = RegionEditorWidget()
        self.dockWidgetContentsRegionEditor.setObjectName("dockWidgetContentsRegionEditor")
        self.dockWidgetRegionEditor.setWidget(self.dockWidgetContentsRegionEditor)
        self.dockWidgetRegionEditor.setHidden(True)

        self.dockWidgetSceneEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetSceneEditor.setWindowTitle('Scene Editor')
        self.dockWidgetSceneEditor.setObjectName("dockWidgetSceneEditor")
        self.dockWidgetContentsSceneEditor = SceneEditorWidget()
        self.dockWidgetContentsSceneEditor.setObjectName("dockWidgetContentsSceneEditor")
        self.dockWidgetSceneEditor.setWidget(self.dockWidgetContentsSceneEditor)
        self.dockWidgetSceneEditor.setHidden(True)

        self.dockWidgetSceneviewerEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetSceneviewerEditor.setWindowTitle('Sceneviewer Editor')
        self.dockWidgetSceneviewerEditor.setObjectName("dockWidgetSceneviewerEditor")
        self.dockWidgetContentsSceneviewerEditor = SceneviewerEditorWidget(self.dockWidgetSceneviewerEditor)
        self.dockWidgetContentsSceneviewerEditor.setObjectName("dockWidgetContentsSceneviewerEditor")
        self.dockWidgetSceneviewerEditor.setWidget(self.dockWidgetContentsSceneviewerEditor)
        self.dockWidgetSceneviewerEditor.setHidden(True)
        self.dockWidgetSceneviewerEditor.visibilityChanged.connect(self.dockWidgetContentsSceneviewerEditor.setEnableUpdates)

        self.dockWidgetSpectrumEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetSpectrumEditor.setWindowTitle('Spectrum Editor')
        self.dockWidgetSpectrumEditor.setObjectName("dockWidgetSpectrumEditor")
        self.dockWidgetContentsSpectrumEditor = SpectrumEditorWidget(self.dockWidgetSpectrumEditor)
        self.dockWidgetContentsSpectrumEditor.setObjectName("dockWidgetContentsSpectrumEditor")
        self.dockWidgetSpectrumEditor.setWidget(self.dockWidgetContentsSpectrumEditor)
        self.dockWidgetSpectrumEditor.setHidden(True)

        self.dockWidgetTessellationEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetTessellationEditor.setWindowTitle('Tessellation Editor')
        self.dockWidgetTessellationEditor.setObjectName("dockWidgetTessellationEditor")
        self.dockWidgetContentsTessellationEditor = TessellationEditorWidget()
        self.dockWidgetContentsTessellationEditor.setObjectName("dockWidgetContentsTessellationEditor")
        self.dockWidgetTessellationEditor.setWidget(self.dockWidgetContentsTessellationEditor)
        self.dockWidgetTessellationEditor.setHidden(True)

        self.dockWidgetTimeEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetTimeEditor.setWindowTitle('Time Editor')
        self.dockWidgetTimeEditor.setObjectName("dockWidgetTimeEditor")
        self.dockWidgetContentsTimeEditor = TimeEditorWidget()
        self.dockWidgetContentsTimeEditor.setObjectName("dockWidgetContentsTimeEditor")
        self.dockWidgetTimeEditor.setWidget(self.dockWidgetContentsTimeEditor)
        self.dockWidgetTimeEditor.setHidden(True)

        self.dockWidgetLoggerEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetLoggerEditor.setWindowTitle('Logger Editor')
        self.dockWidgetLoggerEditor.setObjectName("dockWidgetLoggerEditor")
        self.dockWidgetContentsLoggerEditor = LogViewerWidget()
        self.dockWidgetContentsLoggerEditor.setObjectName("dockWidgetContentsLoggerEditor")
        self.dockWidgetLoggerEditor.setWidget(self.dockWidgetContentsLoggerEditor)
        self.dockWidgetLoggerEditor.setHidden(True)

        self.dockWidgetConsoleEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetConsoleEditor.setWindowTitle('Console Editor')
        self.dockWidgetConsoleEditor.setObjectName("dockWidgetConsoleEditor")
        self.dockWidgetContentsConsoleEditor = ConsoleEditorWidget()
        self.dockWidgetContentsConsoleEditor.setObjectName("dockWidgetContentsConsoleEditor")
        self.dockWidgetConsoleEditor.setWidget(self.dockWidgetContentsConsoleEditor)
        self.dockWidgetConsoleEditor.setHidden(True)

        self.dockWidgetFieldEditor = QtWidgets.QDockWidget(self)
        self.dockWidgetFieldEditor.setWindowTitle('Field Editor')
        self.dockWidgetFieldEditor.setObjectName("dockWidgetFieldEditor")
        self.dockWidgetContentsFieldEditor = FieldListEditorWidget()
        self.dockWidgetContentsFieldEditor.setObjectName("dockWidgetContentsFieldEditor")
        self.dockWidgetFieldEditor.setWidget(self.dockWidgetContentsFieldEditor)
        self.dockWidgetFieldEditor.setHidden(True)

    def _registerEditors(self):
        self._registerEditor(self.dockWidgetMaterialEditor)
        self._registerEditor(self.dockWidgetRegionEditor)
        self._registerEditor(self.dockWidgetSceneEditor)
        self._registerEditor(self.dockWidgetSceneviewerEditor)
        self._registerEditor(self.dockWidgetSpectrumEditor)
        self._registerEditor(self.dockWidgetTessellationEditor)
        self._registerEditor(self.dockWidgetTimeEditor)
        self._registerEditor(self.dockWidgetLoggerEditor)
        self._registerEditor(self.dockWidgetConsoleEditor)
        self._registerEditor(self.dockWidgetFieldEditor)
        self._registerEditor(self.dockWidgetModelSources)

    def _registerEditor(self, editor):
        toggle_action = editor.toggleViewAction()
        toggle_action.triggered.connect(self._view_dock_widget)
        self._toolbar.addAction(toggle_action)
        # view.registerDependentEditor(editor)

    def _clear_views(self):
        self._ui.viewTabWidget.clear()

    def _find_matching_view_widget_index(self, id_):
        for index in range(self._ui.viewTabWidget.count()):
            w = self._ui.viewTabWidget.widget(index)
            if w.getId() == id_:
                return index

        return None

    def _keep_views_with_id(self, keep_ids):
        for keep_id in keep_ids:
            index = self._find_matching_view_widget_index(keep_id)
            if index is not None:
                self._ui.viewTabWidget.removeTab(index)

    def _load_no_views(self):
        add_view = AddView()
        add_view.clicked.connect(self._add_view_clicked)
        self._ui.viewTabWidget.addTab(add_view, "Add View")
        self._set_views_editable(False)

    def _set_views_editable(self, state):
        self._ui.viewTabWidget.setTabsClosable(state)
        tab_bar = self._ui.viewTabWidget.tabBar()
        tab_bar.set_editable(state)

    def _load_views(self):
        document = self._model.getDocument()
        view_manager = document.getViewManager()
        views = view_manager.getViews()

        self._ui.viewTabWidget.blockSignals(True)
        if views:
            active_widget = None
            active_view = view_manager.getActiveView()
            for v in views:
                w = self._create_new_view(v, view_manager.getZincContext())

                if active_view == v.getName():
                    active_widget = w

            if active_widget is not None:
                self._ui.viewTabWidget.setCurrentWidget(active_widget)
            else:
                self._ui.viewTabWidget.setCurrentIndex(0)
            self._set_views_editable(True)
        else:
            self._load_no_views()
        self._ui.viewTabWidget.blockSignals(False)

    def _view_dock_widget(self, show):
        """
        If we are showing the dock widget we will make it current i.e. make sure it is visible if tabbed.
        """
        sender_text = self.sender().text()
        for tab_bar in self.findChildren(QtWidgets.QTabBar):
            for index in range(tab_bar.count()):
                tab_text = tab_bar.tabText(index)
                if tab_text == sender_text:
                    if show:
                        tab_bar.setCurrentIndex(index)
                    elif not tab_bar.currentIndex() == index:
                        self.sender().trigger()
                    return

    def _getEditorAction(self, action_name):
        action = None
        actions = self._toolbar.actions()
        existing_actions = [a for a in actions if a.text() == action_name]
        if existing_actions:
            action = existing_actions[0]
        return action

    def _viewTabTextEdited(self, index, value):
        document = self._model.getDocument()
        view_manager = document.getViewManager()
        active_view_name = view_manager.getActiveView()
        view = view_manager.getView(index)
        if active_view_name == view.getName():
            view_manager.setActiveView(value)
        view.setName(value)

    def _currentViewChanged(self, index):
        document = self._model.getDocument()
        view_manager = document.getViewManager()
        view_manager.setActiveView(self._ui.viewTabWidget.tabText(index))
        self._current_sceneviewer_changed()

    def _setupViews(self):
        icon = QtGui.QIcon(":/widgets/images/icons/list-add-icon.png")
        btn = QtWidgets.QToolButton()
        btn.setStyleSheet("border-radius: 0.75em; border-width: 1px; border-style: solid; border-color: dark-grey;"
                          " background-color: grey; min-width: 1.5em; min-height: 1.5em; margin-right: 1em;")
        btn.setIcon(icon)
        btn.setAutoFillBackground(True)
        btn.clicked.connect(self._add_view_clicked)

        self._ui.viewTabWidget.setCornerWidget(btn)

    def _current_sceneviewer_changed(self):
        try:
            sceneviewer = self._ui.viewTabWidget.currentWidget().getActiveSceneviewer()
        except AttributeError:
            sceneviewer = None

        self.dockWidgetContentsSceneviewerEditor.setSceneviewer(sceneviewer)

    def _visualisationViewReady(self):
        self._visualisation_view_ready = True
        if self._visualisation_view_state_update_pending:
            self._restoreSceneviewerState()

    def registerDoneExecution(self, callback):
        self._callback = callback

    def registerUpdateVisualisationDoc(self, callback):
        self._visualisation_doc_callback = callback

    def _viewTabCloseRequested(self, index):
        document = self._model.getDocument()
        view_manager = document.getViewManager()
        view_manager.removeView(index)
        self._ui.viewTabWidget.removeTab(index)
        if self._ui.viewTabWidget.count() == 0:
            self._load_no_views()

    def _create_new_view(self, view, zinc_context):
        w = ViewWidget(view.getScenes(), view.getGridSpecification(), self._ui.viewTabWidget)

        w.currentChanged.connect(self._current_sceneviewer_changed)
        w.setContext(zinc_context)
        self._ui.viewTabWidget.addTab(w, view.getName())
        return w

    def _add_view_clicked(self):
        dlg = SceneLayoutChooserDialog(self)
        dlg.setModal(True)
        if dlg.exec_():
            layout = dlg.selected_layout()
            document = self._model.getDocument()
            view_manager = document.getViewManager()
            if view_manager.viewCount() == 0:
                self._ui.viewTabWidget.clear()
                self._set_views_editable(True)
            new_view = view_manager.addViewByType(layout)
            view_manager.setActiveView(new_view.getName())
            w = self._create_new_view(new_view, view_manager.getZincContext())
            self._ui.viewTabWidget.setCurrentWidget(w)

    def _documentationButtonClicked(self):
        webbrowser.open("https://abi-mapping-tools.readthedocs.io/en/latest/mapclientplugins.argonviewerstep/docs/index.html")

    def _doneButtonClicked(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            document = self._model.getDocument()
            view_manager = document.getViewManager()
            if view_manager.viewCount():
                self._ui.viewTabWidget.blockSignals(True)
                for index in range(self._ui.viewTabWidget.count()):
                    self._ui.viewTabWidget.setCurrentIndex(index)
                    tab = self._ui.viewTabWidget.widget(index)
                    tab_layout = tab.layout()

                    view = view_manager.getView(index)
                    view.setName(self._ui.viewTabWidget.tabText(index))

                    rows = tab_layout.rowCount()
                    columns = tab_layout.columnCount()
                    for r in range(rows):
                        for c in range(columns):
                            sceneviewer_widget = tab_layout.itemAtPosition(r, c).widget()
                            view.updateSceneviewer(r, c, sceneviewer_widget.get_zinc_sceneviewer())

                self._ui.viewTabWidget.blockSignals(False)

            current_document_location = self._model.getCurrentDocumentLocation()
            self._visualisation_doc_callback(os.path.basename(current_document_location))
            with open(current_document_location, 'w') as f:
                f.write(document.serialize(base_path=os.path.dirname(current_document_location)))

        finally:
            ArgonLogger.closeLogger()
            QtWidgets.QApplication.restoreOverrideCursor()

        self._callback()
