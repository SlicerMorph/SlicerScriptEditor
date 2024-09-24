import os
import slicer
from slicer.ScriptedLoadableModule import *
import logging


class PyFile(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "PyFile"
        self.parent.categories = ["Utilities"]
        self.parent.dependencies = ["Texts"]
        self.parent.contributors = ["Oshane Thomas (SCRI)", "Steve Pieper (Isomic, Inc.)", "Sara Rolfe (SCRI)", "Murat Maga (UW)", "Andras Lasso (PerkLab)"]
        self.parent.helpText = "This module allows reading/writing of .py files and storing them in the scene"
        self.parent.acknowledgementText = """The development of SlicerEditor is supported by funding from the
National Science Foundation through MorphoCloud (DBI/2301405) and the Imageomics Institute (OAC/2118240)."""
        self.parent = parent


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


class PyFileFileReader:
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


class PyFileFileWriter:
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
