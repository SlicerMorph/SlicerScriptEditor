import os
import qt
import slicer
from slicer.ScriptedLoadableModule import *
import logging
from SubjectHierarchyPlugins import AbstractScriptedSubjectHierarchyPlugin

class ViewContextMenu(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = 'PyFile'
        self.parent.categories = ['Utilities']
        self.parent.contributors = ["Oshane Thomas (SCRI), Steve Pieper (Isomics), A. Murat Maga (UW)"]
        self.parent.helpText = '''This module provides a Subject Hierarchy plugin to export vtkMRMLTextNode nodes with 'text/x-python' mimetype as .py files.'''
        self.parent.acknowledgementText = '''Thanks to: Steve Pieper'''
        slicer.app.connect("startupCompleted()", self.onStartupCompleted)

    def onStartupCompleted(self):
        """Register subject hierarchy plugin once app is initialized"""
        print("Startup completed, registering plugin...")
        import SubjectHierarchyPlugins
        from ViewContextMenu import ViewContextMenuSubjectHierarchyPlugin as ViewContextMenuSubjectHierarchyPlugin
        scriptedPlugin = slicer.qSlicerSubjectHierarchyScriptedPlugin(None)
        scriptedPlugin.setPythonSource(ViewContextMenuSubjectHierarchyPlugin.filePath)
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
        pluginHandler.registerPlugin(scriptedPlugin)
        print("ViewContextMenuSubjectHierarchyPlugin loaded and registered")

class ViewContextMenuSubjectHierarchyPlugin(AbstractScriptedSubjectHierarchyPlugin):
    # Necessary static member to be able to set python source to scripted subject hierarchy plugin
    filePath = __file__

    def __init__(self, scriptedPlugin):
        super().__init__(scriptedPlugin)
        self.savePyAction = qt.QAction("Save as .py", scriptedPlugin)
        self.savePyAction.objectName = "SaveAsPyAction"
        # Set the action's position in the menu
        slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(
            self.savePyAction,
            slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode + 5)
        self.savePyAction.connect("triggered()", self.onSavePyAction)
        print("ViewContextMenuSubjectHierarchyPlugin initialized")

    def viewContextMenuActions(self):
        print("Returning context menu actions")
        return [self.savePyAction]

    def showViewContextMenuActionsForItem(self, itemID, eventData=None):
        print(f"showViewContextMenuActionsForItem called for itemID: {itemID}")
        # Get the node associated with the itemID
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        nodeID = shNode.GetItemDataNodeID(itemID)
        node = slicer.mrmlScene.GetNodeByID(nodeID)
        if node:
            print(f"Node found: {node.GetName()}")
            if node.IsA('vtkMRMLTextNode') and node.GetAttribute('mimetype') == 'text/x-python':
                print("Node is a vtkMRMLTextNode with text/x-python mimetype, enabling save as .py action")
                self.savePyAction.setEnabled(True)
            else:
                print("Node is not a vtkMRMLTextNode with text/x-python mimetype, disabling save as .py action")
                self.savePyAction.setEnabled(False)
        else:
            print("No node found for the given itemID")

    def onSavePyAction(self):
        print("Save as .py action triggered")
        itemID = self.subjectHierarchyNode().currentItemID()
        node = slicer.mrmlScene.GetNodeByID(self.subjectHierarchyNode().GetItemDataNodeID(itemID))
        if node:
            self.saveNodeAsPy(node)

    def saveNodeAsPy(self, node):
        writer = PyFileFileWriter(None)
        properties = {'fileName': slicer.app.ioManager().openFileName(None, "Save As", "Python Files (*.py)"),
                      'nodeID': node.GetID()}
        writer.write(properties)

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
