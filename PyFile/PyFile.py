import logging
import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *


class PyFile(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = 'PyFile'
        self.parent.categories = ['Testing.TestCases']
        self.parent.dependencies = []
        self.parent.contributors = ["Oshane Thomas (SCRI), Steve Pieper (Isomics), A. Murat Maga (UW)"]
        self.parent.helpText = '''This module creates a text node from the .py file being imported.'''
        self.parent.acknowledgementText = '''Thanks to: Steve Pieper'''
        self.parent = parent

        # Register the custom file reader
        self.fileReader = PyFileFileReader(parent)

class PyFileWidget(ScriptedLoadableModuleWidget):
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


class PyFileFileReader:
    def __init__(self, parent):
        self.parent = parent

    def description(self):
        return 'PYTHON text node'

    def fileType(self):
        return 'PYTHON'

    def extensions(self):
        return ['PYTHON (*.py)']

    def canLoadFile(self, filePath):
        return filePath.lower().endswith('.py')

    def load(self, properties):
        """
        Uses properties:
            fileName - path to the .py file
        """
        try:
            py_path = properties['fileName']  # py file path

            # Read the content of the .py file
            with open(py_path, 'r') as file:
                content = file.read()

            # Create a new text node and set its content
            text_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTextNode')
            text_node.SetName(os.path.basename(py_path))
            text_node.SetText(content)

            self.parent.loadedNodes = [text_node.GetID()]
            return True

        except Exception as e:
            logging.error('Failed to load file: ' + str(e))
            import traceback
            traceback.print_exc()
            return False
