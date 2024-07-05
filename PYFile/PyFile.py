import logging
import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *


class PYFile(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = 'PyFile'
        parent.categories = ['Testing.TestCases']
        parent.dependencies = []
        parent.contributors = ["Oshane Thomas (SCRI), Steve Pieper (Isomics), A. Murat Maga (UW)"]
        parent.helpText = '''
    This module creates a text node from the .py file being imported.
    '''
        parent.acknowledgementText = '''
    Thanks to:

    Steve Pieper and Andras Lasso (functions from TextureModel module of SlicerIGT used in this script to map texture)
    '''
        self.parent = parent


# def _NIfTIFileInstallPackage():
#   try:
#     import conversion
#   except ModuleNotFoundError:
#     slicer.util.pip_install("git+https://github.com/pnlbwh/conversion.git@v2.3")


class PyFileWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        # Default reload&test widgets are enough.
        # Note that reader and writer is not reloaded.


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
        return True

    def load(self, properties):
        """
    uses properties:
        py_path - path to the .py file
    """
        try:
            py_path = properties['fileName']  # obj file path
            py_dir = os.path.dirname(py_path)
            py_filename = os.path.basename(py_path)
            base_name = os.path.splitext(py_filename)[0]
            extension = os.path.splitext(py_filename)[1]

            # Add model node
            obj_node = slicer.util.loadText(py_path)

        except Exception as e:
            logging.error('Failed to load file: ' + str(e))
            import traceback
            traceback.print_exc()
            return False

        self.parent.loadedNodes = [obj_node.GetID()]
        return True
