import os
import sys
import qt
import slicer
from slicer.ScriptedLoadableModule import *


def getResourceScriptPath(scriptName):
    # Get the path of the module
    modulePath = os.path.dirname(slicer.modules.slicereditor.path)

    # Construct the path to the resource script
    resourceScriptPath = os.path.join(modulePath, 'Resources', 'monaco-editor', scriptName)
    return resourceScriptPath


class SlicerEditor(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "SlicerEditor"
        self.parent.categories = ["SlicerMorph.Input and Output"]
        self.parent.dependencies = []
        self.parent.contributors = ["Murat Maga (UW), Oshane Thomas(SCRI)"]
        self.parent.helpText = """ """
        self.parent.acknowledgementText = """ """


class SlicerEditorWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)
        self.setupSlicerPythonEnvironment()

        # Create and set up the qSlicerWebWidget
        self.editorView = slicer.qSlicerWebWidget()
        self.editorView.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self.editorView.setMinimumSize(qt.QSize(450, 500))

        # Create a label and a dropdown (combobox) with options
        self.comboBoxLabel = qt.QLabel("Python Node:")
        self.fileOptionsDropdown = qt.QComboBox()
        self.fileOptionsDropdown.addItems(["select option", "new .py file", "open .py file", "save as .py file"])
        self.fileOptionsDropdown.currentIndexChanged.connect(self.onFileOptionChanged)

        # Create a horizontal layout for the label and combobox
        self.comboBoxLayout = qt.QHBoxLayout()
        self.comboBoxLayout.addWidget(self.comboBoxLabel)
        self.comboBoxLayout.addWidget(self.fileOptionsDropdown)
        self.comboBoxLayout.addStretch()  # Add stretch to push combobox to the left

        # Create a run button
        self.runButton = qt.QPushButton("Run")
        self.runButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self.runButton.clicked.connect(self.runButtonClicked)

        # Create a save button
        self.saveButton = qt.QPushButton("Save to Scene")
        self.saveButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self.saveButton.clicked.connect(self.saveButtonClicked)

        # Create an import button
        self.importButton = qt.QPushButton("Open from Scene")
        self.importButton.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self.importButton.clicked.connect(self.importButtonClicked)

        # Create a layout to place the buttons next to each other
        self.buttonLayout = qt.QHBoxLayout()
        self.buttonLayout.addWidget(self.runButton)
        self.buttonLayout.addWidget(self.saveButton)
        self.buttonLayout.addWidget(self.importButton)
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
        editorHtmlPath = getResourceScriptPath("index.html")
        self.editorView.url = qt.QUrl.fromLocalFile(editorHtmlPath)

        # Connect the evalResult signal to the slot
        self.editorView.connect("evalResult(QString,QString)", self.onEvalResult)

    def onFileOptionChanged(self, index):
        if index == 1:
            self.newFile()
        elif index == 2:
            self.openFile()
        elif index == 3:
            self.saveFileAs()
        # Reset the combobox to the default option
        self.fileOptionsDropdown.setCurrentIndex(0)

    def newFile(self):
        # Clear the editor
        self.editorView.evalJS("window.editor.getModel().setValue('');")

    def openFile(self):
        # Prompt the user for a filename and location
        filePath, _ = qt.QFileDialog.getOpenFileName(slicer.util.mainWindow(), 'Open', '', 'Python Files (*.py)')
        if not filePath:
            return

        # Read the file and set its content to the editor
        with open(filePath, 'r') as file:
            code = file.read()
        self.editorView.evalJS(f"window.editor.getModel().setValue(`{code}`);")

    def saveFileAs(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")
        self.savingToFileAs = True

    def runButtonClicked(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")

    def saveButtonClicked(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")
        self.savingCode = True

    def importButtonClicked(self):
        # Get the text node from the user
        textNodes = slicer.util.getNodesByClass("vtkMRMLTextNode")
        if not textNodes:
            qt.QMessageBox.information(slicer.util.mainWindow(), 'SlicerEditor', 'No text nodes found in the scene.')
            return

        # Let the user select a node
        items = [''] + [node.GetName() for node in textNodes]
        item = qt.QInputDialog.getItem(slicer.util.mainWindow(), 'Select Text Node', 'Select a text node to open:',
                                       items, 0, False)

        if item == '':
            pass
        else:
            selectedNode = next(node for node in textNodes if node.GetName() == item)
            code = selectedNode.GetText()
            self.editorView.evalJS(f"window.editor.getModel().setValue(`{code}`);")

    def onEvalResult(self, request, result):
        if request == "window.editor.getModel().getValue()":
            if hasattr(self, 'savingCode') and self.savingCode:
                self.saveEditorCodeToScene(result)
                self.savingCode = False
            elif hasattr(self, 'savingToFileAs') and self.savingToFileAs:
                self.saveEditorCodeToFileAs(result)
                self.savingToFileAs = False
            else:
                self.processEditorCode(result)

    def saveEditorCodeToScene(self, code):
        if not code:
            print("No code to save.")
            return
        else:
            # Prompt the user for a filename
            filePath, ok = qt.QInputDialog.getText(slicer.util.mainWindow(), 'Save As', 'Enter filename:')
            if ok and filePath:
                if not filePath.endswith('.py'):
                    filePath += '.py'
                # Create a new text node
                textNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTextNode")
                textNode.SetName(filePath)
                textNode.SetText(code)
                print(f"Code saved to MRML text node: {textNode.GetName()}")

    def saveEditorCodeToFileAs(self, code):
        if not code:
            print("No code to save.")
            return
        else:
            # Prompt the user for a filename and location
            filePath = qt.QFileDialog.getSaveFileName(slicer.util.mainWindow(), 'Save As', '',
                                                          'Python Files (*.py)')
            if filePath:
                if not filePath.endswith('.py'):
                    filePath += '.py'
                # Save the code to the specified file
                with open(filePath, 'w') as file:
                    file.write(code)
                print(f"Code saved to file: {filePath}")

    @staticmethod
    def processEditorCode(code):
        if not code:
            print("No code to execute.")
            return
        elif code:
            slicer.app.pythonManager().executeString(code)
        else:
            print("In Slicer you would have executed this code:")
            print(code)

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
                os.path.join(slicer.app.slicerHome, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}',
                             'site-packages')
            ]
        for path in slicer_paths:
            if path not in sys.path:
                sys.path.append(path)
        os.environ['PYTHONPATH'] = os.pathsep.join(slicer_paths)


class SlicerEditorLogic(ScriptedLoadableModuleLogic):
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
        ScriptedLoadableModuleLogic.__init__(self)
