import os
import logging
import sys
import qt
import slicer
from slicer.ScriptedLoadableModule import *

def getIndexPath(scriptName):
    # Get the path of the module
    modulePath = os.path.dirname(slicer.modules.scripteditor.path)

    # Construct the path to the resource script
    resourceScriptPath = os.path.join(modulePath, 'Resources', 'monaco-editor', scriptName)
    return resourceScriptPath


class ScriptEditor(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Script Editor"
        self.parent.categories = ["Utilities"]
        self.parent.dependencies = ["Texts", "SubjectHierarchy"]
        self.parent.contributors = ["Oshane Thomas (SCRI)", "Steve Pieper (Isomic, Inc.)", "Sara Rolfe (SCRI)", "Andras Lasso (PerkLab)", "Murat Maga (UW)"]
        self.parent.helpText = """The Script Editor module provides an integrated development environment within 3D 
Slicer for editing, debugging, and running Python scripts, enhancing the scripting capabilities for users and developers."""
        self.parent.acknowledgementText = """The development of ScriptEditor is supported by funding from the
National Science Foundation through MorphoCloud (DBI/2301405) and the Imageomics Institute (OAC/2118240)."""

    def onStartupCompleted():
        """Register subject hierarchy plugin once app is initialized"""
        from ScriptEditorLib import ScriptEditorSubjectHierarchyPlugin
        scriptedPlugin = slicer.qSlicerSubjectHierarchyScriptedPlugin(None)
        scriptedPlugin.name = "SavePyFile"
        scriptedPlugin.setPythonSource(ScriptEditorSubjectHierarchyPlugin.ScriptEditorSubjectHierarchyPlugin.filePath)
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
        pluginHandler.registerPlugin(scriptedPlugin)

    slicer.app.connect("startupCompleted()", onStartupCompleted)

    # def setup(self):
    #     # Register subject hierarchy plugin
    #     from ScriptEditorPlugins import ScriptEditorSubjectHierarchyPlugin

    #     scriptedPlugin = slicer.qSlicerSubjectHierarchyScriptedPlugin(None)

    #     scriptedPlugin.setPythonSource(ScriptEditorSubjectHierarchyPlugin.filePath)


class ScriptEditorWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.copyCode = None
        self.savingCode = None
        self.code_history = []

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)
        self.setupSlicerPythonEnvironment()

        # Create and set up the qSlicerWebWidget
        self.editorView = slicer.qSlicerWebWidget()
        self.editorView.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self.editorView.setMinimumSize(qt.QSize(200, 350))

        # Initially disable the editor view
        self.editorView.setEnabled(False)

        # Create a label and a qMRMLNodeComboBox for text nodes with "text/x-python" mimetype
        self.comboBoxLabel = qt.QLabel("Script Node:")
        self.nodeComboBox = slicer.qMRMLNodeComboBox()
        self.nodeComboBox.nodeTypes = ["vtkMRMLTextNode"]
        self.nodeComboBox.addAttribute("vtkMRMLTextNode", "mimetype", "text/x-python")
        self.nodeComboBox.showChildNodeTypes = False
        self.nodeComboBox.showHidden = False
        self.nodeComboBox.showChildNodeTypes = False
        self.nodeComboBox.selectNodeUponCreation = True
        self.nodeComboBox.noneEnabled = True
        self.nodeComboBox.removeEnabled = True
        self.nodeComboBox.renameEnabled = True
        self.nodeComboBox.addEnabled = True
        self.nodeComboBox.noneDisplay = "(Create New Python Text Node)"
        self.nodeComboBox.setMRMLScene(slicer.mrmlScene)
        self.nodeComboBox.connect("currentNodeChanged(vtkMRMLNode*)", self.onNodeSelected)
        self.nodeComboBox.connect("nodeAdded(vtkMRMLNode*)", self.onNodeAdded)

        # Create a horizontal layout for the label and qMRMLNodeComboBox
        self.comboBoxLayout = qt.QHBoxLayout()
        self.comboBoxLayout.addWidget(self.comboBoxLabel)
        self.comboBoxLayout.addWidget(self.nodeComboBox)
        self.comboBoxLayout.addStretch()  # Add stretch to push combobox to the left

        # Create run, save, and copy buttons
        # self.runButton = qt.QPushButton("Run")
        # self.runButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        # self.runButton.setEnabled(False)  # Disable the button initially
        # self.runButton.clicked.connect(self.runButtonClicked)

        self.saveButton = qt.QPushButton("Save")
        self.saveButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self.saveButton.setEnabled(False)  # Disable the button initially
        self.saveButton.clicked.connect(self.saveButtonClicked)

        self.copyButton = qt.QPushButton("Copy")
        self.copyButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self.copyButton.setEnabled(False)  # Disable the button initially
        self.copyButton.clicked.connect(self.copyButtonClicked)

        # Create a layout to place the buttons next to each other
        self.buttonLayout = qt.QHBoxLayout()
        # self.buttonLayout.addWidget(self.runButton)
        self.buttonLayout.addWidget(self.saveButton)
        self.buttonLayout.addWidget(self.copyButton)
        self.buttonLayout.addStretch()  # Add stretch to push buttons to the left

        self.buttonWidget = qt.QWidget()
        self.buttonWidget.setLayout(self.buttonLayout)

        # Main layout
        self.mainLayout = qt.QVBoxLayout()
        self.mainLayout.addLayout(self.comboBoxLayout)  # Add the comboBox layout to the main layout
        self.mainLayout.addWidget(self.buttonWidget)
        self.mainLayout.addWidget(self.editorView)

        # Set the layout to the module widget
        self.layout.addLayout(self.mainLayout)

        # Load the Monaco Editor HTML
        editorHtmlPath = getIndexPath("index.html")
        self.editorView.url = qt.QUrl.fromLocalFile(editorHtmlPath)

        # Connect the evalResult signal to the slot
        self.editorView.connect("evalResult(QString,QString)", self.onEvalResult)

    def onNodeSelected(self):
        # Get the selected node
        selectedNode = self.nodeComboBox.currentNode()
        if selectedNode:
            self.editorView.setEnabled(True)  # Enable the editor view
            # self.runButton.setEnabled(True)  # Enable the run button
            self.saveButton.setEnabled(True)  # Enable the save button
            self.copyButton.setEnabled(True)  # Enable the copy button
            code = selectedNode.GetText()
            self.editorView.evalJS(f"window.editor.getModel().setValue(`{code}`);")
        else:
            self.editorView.setEnabled(False)  # Disable the editor view
            # self.runButton.setEnabled(False)  # Disable the run button
            self.saveButton.setEnabled(False)  # Disable the save button
            self.copyButton.setEnabled(False)  # Disable the copy button
            self.editorView.evalJS("window.editor.getModel().setValue('');")  # Clear the editor

    def onNodeAdded(self, node):
        if isinstance(node, slicer.vtkMRMLTextNode):
            storageNode = slicer.vtkMRMLTextStorageNode()
            slicer.mrmlScene.AddNode(storageNode)
            node.SetAndObserveStorageNodeID(storageNode.GetID())

    def runButtonClicked(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")

    def saveButtonClicked(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")
        self.savingCode = True  # set save bool

    def copyButtonClicked(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")
        self.copyCode = True  # set save bool

    def onEvalResult(self, request, result):
        if request == "window.editor.getModel().getValue()":
            if self.savingCode:
                self.saveEditorContent(result)
                self.savingCode = False
            elif self.copyCode:
                self.code_history.append(result)
                self.copyToClipboard(result)
                self.copyCode = False
            else:
                self.code_history.append(result)
                self.processEditorCode(result)
                self.copyToClipboard(result)

    @staticmethod
    def processEditorCode(code):
        if not code:
            print("No code to execute.")
            return
        else:
            slicer.app.pythonConsole().printOutputMessage(code)
            slicer.app.pythonManager().executeString(code)

    def saveEditorContent(self, code):
        selectedNode = self.nodeComboBox.currentNode()
        if selectedNode:
            selectedNode.SetText(code)
            print(f"Code saved to node: {selectedNode.GetName()}")
        else:
            print("No node selected to save the code.")

    def copyToClipboard(self, code):
        clipboard = qt.QApplication.clipboard()
        clipboard.setText(code)
        print("Code copied to clipboard.")

    def setCurrentNode(self, node):
        """Sets the current node in the nodeComboBox."""
        self.nodeComboBox.setCurrentNode(node)

    @staticmethod
    def setupSlicerPythonEnvironment():
        import platform
        slicer_paths = []
        if platform.system() == 'Windows':
            slicer_paths = [
                os.path.join(slicer.app.slicerHome, 'bin', 'Python',
                             f'lib\\python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
            ]
        else:
            slicer_paths = [
                os.path.join(slicer.app.slicerHome, 'lib',
                             f'python{sys.version_info.major}.{sys.version_info.minor}',
                             'site-packages')
            ]
        for path in slicer_paths:
            if path not in sys.path:
                sys.path.append(path)
        os.environ['PYTHONPATH'] = os.pathsep.join(slicer_paths)


class ScriptEditorLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__()

def _createPythonScriptStorageNode(text_node, py_path):
    storage_node = text_node.GetStorageNode()
    if not storage_node:
        storage_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTextStorageNode')
    storage_node.SetFileName(py_path)
    if hasattr(storage_node, "SetSupportedReadFileExtensions"):
        storage_node.SetSupportedReadFileExtensions(["py"])
        storage_node.SetSupportedWriteFileExtensions(["py"])
    else:
        logging.warning("This Slicer version does not support saving of Python scripts as .py files in the scene")
    text_node.SetAndObserveStorageNodeID(storage_node.GetID())
    return storage_node


class ScriptEditorFileReader:
    def __init__(self, parent):
        self.parent = parent

    def description(self):
        return 'Python Script'

    def fileType(self):
        return 'PythonScript'

    def extensions(self):
        return ['Python Script (.py)']

    def canLoadFileConfidence(self, filePath):
        return 1.5 if filePath.lower().endswith('.py') else 0.0

    def load(self, properties):
        try:
            py_path = properties['fileName']

            text_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTextNode')
            text_node.SetAttribute("mimetype", "text/x-python")  # Setting the mimetype attribute
            text_node.SetAttribute("customTag", "pythonFile")  # Custom tag for additional signaling

            # Create and configure a storage node for the text node
            storage_node = _createPythonScriptStorageNode(text_node, py_path)

            text_node.SetName(storage_node.GetFileNameWithoutExtension())

            if not storage_node.ReadData(text_node):
                return False

            self.parent.loadedNodes = [text_node.GetID()]

            # Notify the subject hierarchy about the new node
            pluginHandlerSingleton = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
            shNode = pluginHandlerSingleton.subjectHierarchyNode()
            shNode.RequestOwnerPluginSearch(text_node)  # Update the subject hierarchy

            return True

        except Exception as e:
            logging.error('Failed to load file: ' + str(e))
            import traceback
            traceback.print_exc()
            return False


class ScriptEditorFileWriter:
    def __init__(self, parent):
        self.parent = parent

    def description(self):
        return "Python Script"

    def fileType(self):
        return "PythonScript"

    def extensions(self, obj):
        return ['Python Script (.py)']
    
    def canWriteObjectConfidence(self, obj):
        # Select this custom reader by default by returning higher confidence than default
        canWrite = obj.IsA('vtkMRMLTextNode') and obj.GetAttribute('mimetype') == 'text/x-python'
        return 1.5 if canWrite else 0.3

    def write(self, properties):
        try:
            py_path = properties['fileName']
            node_id = properties['nodeID']
            text_node = slicer.mrmlScene.GetNodeByID(node_id)

            if text_node is None:
                logging.error('Failed to get node by ID: ' + node_id)
                return False

            storage_node = _createPythonScriptStorageNode(text_node, py_path)
            if not storage_node.WriteData(text_node):
                return False

            self.parent.writtenNodes = [node_id]
            return True

        except Exception as e:
            logging.error('Failed to write file: ' + str(e))
            import traceback
            traceback.print_exc()
            return False
