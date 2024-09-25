import logging
import os
import qt

import slicer
from slicer.i18n import tr as _

from AbstractScriptedSubjectHierarchyPlugin import *


class ScriptEditorSubjectHierarchyPlugin(AbstractScriptedSubjectHierarchyPlugin):
    # Necessary static member to be able to set python source to scripted subject hierarchy plugin
    filePath = __file__
    fileIcon = None

    def __init__(self, scriptedPlugin):
        AbstractScriptedSubjectHierarchyPlugin.__init__(self, scriptedPlugin)

        pluginHandlerSingleton = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
        self.subjectHierarchyNode = pluginHandlerSingleton.subjectHierarchyNode()

        self.initializeIcon()

    def initializeIcon(self):
        iconPath = os.path.join(os.path.dirname(slicer.modules.scripteditor.path), "Resources", "Icons", "PythonFile.png")
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

    def editNodeInScriptEditor(self, node):
        editorModule = slicer.modules.scripteditor
        slicer.util.selectModule(editorModule.name)

        editorWidget = slicer.modules.scripteditor.widgetRepresentation().self()

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
            self.editNodeInScriptEditor(node)
