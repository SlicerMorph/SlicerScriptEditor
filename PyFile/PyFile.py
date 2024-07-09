import os
import slicer
from slicer.ScriptedLoadableModule import *
import logging


class PyFile(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = 'PyFile'
        self.parent.categories = ['PyFile']
        self.parent.dependencies = []
        self.parent.contributors = ["Oshane Thomas (SCRI), Steve Pieper (Isomics), A. Murat Maga (UW)"]
        self.parent.helpText = '''This module creates a text node from the .py file being imported.'''
        self.parent.acknowledgementText = '''Thanks to: Steve Pieper'''
        self.parent = parent

        # Register the custom file reader
        self.fileReader = PyFileFileReader(parent)
        self.fileWriter = PyFileFileWriter(parent)


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
        return 'PYTHON Script'

    def fileType(self):
        return 'PYTHON'

    def extensions(self):
        return ['PYTHON (*.py)']

    def canLoadFile(self, filePath):
        return filePath.lower().endswith('.py')

    def load(self, properties):
        try:
            py_path = properties['fileName']

            with open(py_path, 'r') as file:
                content = file.read()

            text_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTextNode')
            text_node.SetName(os.path.basename(py_path))
            text_node.SetText(content)
            text_node.SetAttribute("mimetype", "text/x-python")

            self.parent.loadedNodes = [text_node.GetID()]
            return True

        except Exception as e:
            logging.error('Failed to load file: ' + str(e))
            import traceback
            traceback.print_exc()
            return False


class PyFileFileWriter:
    def __init__(self, parent):
        self.parent = parent

    def description(self):
        return 'PYTHON Script'

    def fileType(self):
        return 'PYTHON'

    def extensions(self):
        return ['PYTHON (*.py)']

    def canWriteObject(self, object):
        return object.IsA('vtkMRMLTextNode') and object.GetAttribute('mimetype') == 'text/x-python'

    def write(self, properties):
        try:
            py_path = properties['fileName']
            node_id = properties['nodeID']
            text_node = slicer.mrmlScene.GetNodeByID(node_id)

            if text_node is None:
                logging.error('Failed to get node by ID: ' + node_id)
                return False

            content = text_node.GetText()
            with open(py_path, 'w') as file:
                file.write(content)

            return True

        except Exception as e:
            logging.error('Failed to write file: ' + str(e))
            import traceback
            traceback.print_exc()
            return False
