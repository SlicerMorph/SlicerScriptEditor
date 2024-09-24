import os, time
import qt, vtk
import slicer
from slicer.ScriptedLoadableModule import *
import logging
from SubjectHierarchyPlugins import AbstractScriptedSubjectHierarchyPlugin


class SavePyFile(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = 'SavePyFile'
        self.parent.categories = ['Utilities']
        self.parent.contributors = ["Oshane Thomas(SCRI), Steve Pieper (Isomic, Inc.), Sara Rolfe (SCRI), Murat Maga "
                                    "(UW)"]
        self.parent.helpText = '''This module provides a Subject Hierarchy plugin to export vtkMRMLTextNode nodes with 'text/x-python' mimetype as .py files.'''
        self.parent.acknowledgementText = """The development of SlicerEditor is supported by funding from the 
        National Science Foundation through MorphoCloud (DBI/2301405) and the Imageomics Institute (OAC/2118240)."""

        def onStartupCompleted():
            """Register subject hierarchy plugin once app is initialized"""
            import SubjectHierarchyPlugins
            from SavePyFile import SavePyFileSubjectHierarchyPlugin
            scriptedPlugin = slicer.qSlicerSubjectHierarchyScriptedPlugin(None)
            scriptedPlugin.name = "SavePyFile"
            scriptedPlugin.setPythonSource(SavePyFileSubjectHierarchyPlugin.filePath)
            pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
            pluginHandler.registerPlugin(scriptedPlugin)

        slicer.app.connect("startupCompleted()", onStartupCompleted)


class SavePyFileSubjectHierarchyPlugin(AbstractScriptedSubjectHierarchyPlugin):
    # Necessary static member to be able to set python source to scripted subject hierarchy plugin
    filePath = __file__
    fileIcon = None

    def __init__(self, scriptedPlugin):
        AbstractScriptedSubjectHierarchyPlugin.__init__(self, scriptedPlugin)

        pluginHandlerSingleton = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
        self.subjectHierarchyNode = pluginHandlerSingleton.subjectHierarchyNode()

        self.initializeIcon()

        self.savePyAction = qt.QAction("Save as .py", scriptedPlugin)
        self.savePyAction.objectName = "SaveAsPyAction"

        self.savePyAction.connect("triggered()", self.onSavePyAction)

    def initializeIcon(self):
        iconPath = os.path.join(os.path.dirname(slicer.modules.pyfile.path), 'Resources', 'python_icon.png')
        self.fileIcon = qt.QIcon(iconPath)

    def canOwnSubjectHierarchyItem(self, itemID):
        pluginHandlerSingleton = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
        pluginHandlerSingleton.subjectHierarchyNode().Modified()  # Refresh the subject hierarchy node
        shNode = pluginHandlerSingleton.subjectHierarchyNode()
        node = shNode.GetItemDataNode(itemID)

        if node:
            mimetype = node.GetAttribute("mimetype")
            fileType = node.GetAttribute("fileType")
            if mimetype == "text/x-python" or fileType == "python":
                return 1.

        # else:
        #     print("No node found for itemID:", itemID)
        return 0.0

    def icon(self, itemID):
        pluginHandlerSingleton = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
        shNode = pluginHandlerSingleton.subjectHierarchyNode()
        node = shNode.GetItemDataNode(itemID)

        if node and (node.GetAttribute("mimetype") == "text/x-python" or node.GetAttribute("fileType") == "python"):
            return self.fileIcon

        # Check the file extension of the storage node
        storageNodeID = node.GetStorageNodeID()
        if storageNodeID:
            storageNode = slicer.mrmlScene.GetNodeByID(storageNodeID)
            if storageNode and storageNode.GetFileName().lower().endswith('.py'):
                return self.fileIcon

        return qt.QIcon()

    def visibilityIcon(self, visible):
        return qt.QIcon()

    def itemContextMenuActions(self):
        return [self.savePyAction]

    def showContextMenuActionsForItem(self, itemID):

        # Reset all menus
        self.savePyAction.visible = False
        self.savePyAction.enabled = False

        # Get the node associated with the itemID
        node = self.subjectHierarchyNode.GetItemDataNode(itemID)
        if node:
            if node.IsA('vtkMRMLTextNode') and node.GetAttribute('mimetype') == 'text/x-python':
                self.savePyAction.enabled = True
                self.savePyAction.visible = True
            else:
                self.savePyAction.enabled = False
                self.savePyAction.visible = False
        else:
            print("No node found for the given itemID")

    def onSavePyAction(self):
        pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
        currentItemID = pluginHandler.currentItem()
        node = self.subjectHierarchyNode.GetItemDataNode(currentItemID)

        if node:
            self.saveNodeAsPy(node)

    def saveNodeAsPy(self, node):
        writer = PyFileFileWriter(None)
        initialFileName = node.GetName()
        if not initialFileName.endswith(".py"):
            initialFileName += ".py"
        saveFileName = qt.QFileDialog.getSaveFileName(None, "Save As", initialFileName, "Python Files (*.py)")
        if saveFileName:
            properties = {'fileName': saveFileName, 'nodeID': node.GetID()}
            writer.write(properties)

    def editNodeInSlicerEditor(self, node):
        editorModule = slicer.modules.slicereditor
        slicer.util.selectModule(editorModule.name)

        editorWidget = slicer.modules.slicereditor.widgetRepresentation().self()

        # Set the node in the combo box
        editorWidget.setCurrentNode(node)

        code = node.GetText().replace('\\', '\\\\').replace('`', '\\`').replace('"',
                                                                                '\\"')  # Escape backslashes, backticks, and double quotes

        def setEditorContent():
            jsSetEditorContent = f"""
                (function setEditorContent() {{
                    if (window.editor && window.editor.getModel()) {{
                        window.editor.getModel().setValue(`{code}`);
                    }} else {{
                        setTimeout(setEditorContent, 100);
                    }}
                }})();
            """
            editorWidget.editorView.evalJS(jsSetEditorContent)

        # Adding a slight delay to ensure the editor is initialized
        qt.QTimer.singleShot(500, setEditorContent)

    def editProperties(self, itemID):
        node = self.subjectHierarchyNode.GetItemDataNode(itemID)
        if node:
            self.editNodeInSlicerEditor(node)
