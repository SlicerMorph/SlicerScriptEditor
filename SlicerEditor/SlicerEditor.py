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

        self.mainLayout = qt.QVBoxLayout()
        self.mainLayout.addWidget(self.buttonWidget)
        self.mainLayout.addWidget(self.editorView)

        # Set the layout to the module widget
        self.layout.addLayout(self.mainLayout)

        # Load the Monaco Editor HTML
        editorHtmlPath = getResourceScriptPath("index.html")
        self.editorView.url = qt.QUrl.fromLocalFile(editorHtmlPath)

        # Connect the evalResult signal to the slot
        self.editorView.connect("evalResult(QString,QString)", self.onEvalResult)

    def runButtonClicked(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")

    def saveButtonClicked(self):
        # Execute the JavaScript to get the code from the editor
        self.editorView.evalJS("window.editor.getModel().getValue()")
        self.savingCode = True

    def importButtonClicked(self):
        # Get the text node from the user
        # Get all text nodes in the scene
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
                self.saveEditorCode(result)
                self.savingCode = False
            else:
                self.processEditorCode(result)

    def saveEditorCode(self, code):
        if not code:
            print("No code to save.")
            return
        else:
            # Prompt the user for a filename
            filePath = qt.QInputDialog.getText(slicer.util.mainWindow(), 'Save As', 'Enter filename:')
            if filePath.split('.')[-1] == 'py':
                # Create a new text node
                textNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTextNode")
                textNode.SetName(filePath)
                textNode.SetText(code)
                print(f"Code saved to MRML text node: {textNode.GetName()}")
            else:
                # Create a new text node
                textNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTextNode")
                textNode.SetName(filePath + '.py')
                textNode.SetText(code)
                print(f"Code saved to MRML text node: {textNode.GetName()}")

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