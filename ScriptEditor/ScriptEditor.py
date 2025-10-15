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

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)
        self.setupSlicerPythonEnvironment()
        
        # Load saved settings
        settings = qt.QSettings()
        self.savedSaveLocation = settings.value("ScriptEditor/SaveLocation", "")

        # Create and set up the qSlicerWebWidget
        self.editorView = slicer.qSlicerWebWidget()
        self.editorView.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self.editorView.setMinimumSize(qt.QSize(200, 350))

        # Initially disable the editor view
        self.editorView.setEnabled(False)

        # Create a label and a qMRMLNodeComboBox for text nodes with "text/x-python" mimetype
        self.comboBoxLabel = qt.QLabel("Script:")
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
        self.nodeComboBox.baseName = "Script"
        self.nodeComboBox.noneDisplay = "(Create New Python Script)"
        self.nodeComboBox.setMRMLScene(slicer.mrmlScene)
        
        self.nodeComboBox.connect("currentNodeChanged(vtkMRMLNode*)", self.onNodeSelected)
        self.nodeComboBox.connect("nodeAdded(vtkMRMLNode*)", self.onNodeAdded)

        # Create a horizontal layout for the label and qMRMLNodeComboBox
        self.comboBoxLayout = qt.QHBoxLayout()
        self.comboBoxLayout.addWidget(self.comboBoxLabel)
        self.comboBoxLayout.addWidget(self.nodeComboBox)
        self.comboBoxLayout.addStretch()  # Add stretch to push combobox to the left

        # Create theme selector with radio buttons
        self.themeLabel = qt.QLabel("Theme:")
        self.lightThemeRadio = qt.QRadioButton("Light")
        self.darkThemeRadio = qt.QRadioButton("Dark")
        self.lightThemeRadio.setChecked(True)  # Default to light theme
        self.lightThemeRadio.toggled.connect(self.onThemeChanged)
        self.darkThemeRadio.toggled.connect(self.onThemeChanged)
        
        # Create font size slider
        self.fontSizeLabel = qt.QLabel("Font Size:")
        self.fontSizeSlider = qt.QSlider(qt.Qt.Horizontal)
        self.fontSizeSlider.setMinimum(8)
        self.fontSizeSlider.setMaximum(32)
        self.fontSizeSlider.setValue(14)  # Default font size
        self.fontSizeSlider.setTickPosition(qt.QSlider.TicksBelow)
        self.fontSizeSlider.setTickInterval(4)
        self.fontSizeSlider.setMaximumWidth(150)
        self.fontSizeSlider.valueChanged.connect(self.onFontSizeChanged)
        
        self.fontSizeValueLabel = qt.QLabel("14")
        self.fontSizeValueLabel.setMinimumWidth(25)
        
        self.settingsLayout = qt.QHBoxLayout()
        self.settingsLayout.addWidget(self.themeLabel)
        self.settingsLayout.addWidget(self.lightThemeRadio)
        self.settingsLayout.addWidget(self.darkThemeRadio)
        self.settingsLayout.addWidget(qt.QLabel("  |  "))  # Separator
        self.settingsLayout.addWidget(self.fontSizeLabel)
        self.settingsLayout.addWidget(self.fontSizeSlider)
        self.settingsLayout.addWidget(self.fontSizeValueLabel)
        self.settingsLayout.addStretch()

        self.settingsWidget = qt.QWidget()
        self.settingsWidget.setLayout(self.settingsLayout)

        # Create save location selector
        self.saveLocationLabel = qt.QLabel("Save Location:")
        self.saveLocationPathEdit = qt.QLineEdit()
        self.saveLocationPathEdit.setReadOnly(True)
        self.saveLocationPathEdit.setPlaceholderText("No location set (will prompt on save)")
        
        # Restore saved location
        if self.savedSaveLocation:
            self.saveLocationPathEdit.setText(self.savedSaveLocation)
        
        self.saveLocationBrowseButton = qt.QPushButton("Browse...")
        self.saveLocationBrowseButton.clicked.connect(self.onBrowseSaveLocation)
        self.saveLocationBrowseButton.setToolTip("Choose a folder to save scripts")
        
        self.saveLocationLayout = qt.QHBoxLayout()
        self.saveLocationLayout.addWidget(self.saveLocationLabel)
        self.saveLocationLayout.addWidget(self.saveLocationPathEdit)
        self.saveLocationLayout.addWidget(self.saveLocationBrowseButton)
        
        self.saveLocationWidget = qt.QWidget()
        self.saveLocationWidget.setLayout(self.saveLocationLayout)

        # Main layout
        self.mainLayout = qt.QVBoxLayout()
        self.mainLayout.addLayout(self.comboBoxLayout)  # Add the comboBox layout to the main layout
        self.mainLayout.addWidget(self.settingsWidget)
        self.mainLayout.addWidget(self.saveLocationWidget)
        self.mainLayout.addWidget(self.editorView)

        # Set the layout to the module widget
        self.layout.addLayout(self.mainLayout)

        # Load the Monaco Editor HTML
        editorHtmlPath = getIndexPath("index.html")
        self.editorView.url = qt.QUrl.fromLocalFile(editorHtmlPath)

        # Connect the evalResult signal to the slot
        self.editorView.connect("evalResult(QString,QString)", self.onEvalResult)
        
        # Add a delay to ensure Monaco editor is fully loaded before setup
        qt.QTimer.singleShot(3000, self.setupEditorFeatures)

    def onBrowseSaveLocation(self):
        """Open a dialog to choose save location for scripts"""
        currentPath = self.saveLocationPathEdit.text
        if not currentPath or currentPath == "No location set (will prompt on save)":
            currentPath = os.path.expanduser("~")
        
        directory = qt.QFileDialog.getExistingDirectory(
            self.parent,
            "Choose Save Location for Scripts",
            currentPath
        )
        
        if directory:
            self.saveLocationPathEdit.setText(directory)
            print(f"Scripts will be saved to: {directory}")
            
            # Save the setting persistently
            settings = qt.QSettings()
            settings.setValue("ScriptEditor/SaveLocation", directory)
            
            # Update the current node's storage node with the new location
            selectedNode = self.nodeComboBox.currentNode()
            if selectedNode:
                storageNode = selectedNode.GetStorageNode()
                if storageNode:
                    existingFileName = storageNode.GetFileName()
                    # Only update if there's no existing file (i.e., it's a new script)
                    if not existingFileName or existingFileName == "":
                        nodeName = selectedNode.GetName() if selectedNode.GetName() else "Script"
                        safeName = "".join(c for c in nodeName if c.isalnum() or c in (' ', '_', '-')).strip()
                        if not safeName:
                            safeName = "Script"
                        newFileName = os.path.join(directory, f"{safeName}.py")
                        storageNode.SetFileName(newFileName)
                        print(f"File path set to: {newFileName}")
            
            # Update all existing script nodes that don't have a file location
            self.updateAllScriptNodeLocations(directory)
    
    def updateAllScriptNodeLocations(self, directory):
        """Update all script nodes without existing file locations to use the new directory"""
        # Find all text nodes with python mimetype
        collection = slicer.mrmlScene.GetNodesByClass("vtkMRMLTextNode")
        collection.UnRegister(None)
        
        for i in range(collection.GetNumberOfItems()):
            node = collection.GetItemAsObject(i)
            if node.GetAttribute("mimetype") == "text/x-python":
                storageNode = node.GetStorageNode()
                if storageNode:
                    existingFileName = storageNode.GetFileName()
                    # Only update if there's no existing file
                    if not existingFileName or existingFileName == "":
                        nodeName = node.GetName() if node.GetName() else "Script"
                        safeName = "".join(c for c in nodeName if c.isalnum() or c in (' ', '_', '-')).strip()
                        if not safeName:
                            safeName = "Script"
                        newFileName = os.path.join(directory, f"{safeName}.py")
                        storageNode.SetFileName(newFileName)

    def setupEditorFeatures(self):
        """Setup editor features after Monaco is fully loaded"""
        self.setupContextMenu()
        self.setTheme("vs")  # Set default light theme
        self.setupChangeDetection()  # Set up change detection for marking nodes as modified
    
    def setupChangeDetection(self):
        """Setup Monaco editor to detect content changes and mark node as modified"""
        changeDetectionScript = """
        (function() {
            if (!window.editor) {
                console.log('Editor not ready for change detection, retrying in 1 second...');
                setTimeout(arguments.callee, 1000);
                return;
            }
            
            // Track if content has changed
            window.editorContentChanged = false;
            
            // Listen for content changes
            window.editor.onDidChangeModelContent(function(e) {
                window.editorContentChanged = true;
            });
            
            console.log('Change detection initialized');
        })();
        """
        self.editorView.evalJS(changeDetectionScript)
        
        # Set up a timer to periodically check for changes and mark node as modified
        self.changeCheckTimer = qt.QTimer()
        self.changeCheckTimer.timeout.connect(self.checkForContentChanges)
        self.changeCheckTimer.start(1000)  # Check every second
        self._checkingChanges = False
        self._updatingFromChangeDetection = False
    
    def checkForContentChanges(self):
        """Check if content has changed and mark node as modified"""
        if self._checkingChanges:
            return
        self._checkingChanges = True
        self.editorView.evalJS("window.editorContentChanged || false")
    
    def onThemeChanged(self):
        """Handle theme radio button changes"""
        if self.lightThemeRadio.isChecked():
            self.setTheme("vs")  # Light theme
        else:
            self.setTheme("vs-dark")  # Dark theme
    
    def onFontSizeChanged(self, value):
        """Handle font size slider changes"""
        self.fontSizeValueLabel.setText(str(value))
        self.setFontSize(value)
    
    def setFontSize(self, size):
        """Set the Monaco editor font size"""
        fontSizeScript = f"""
        (function() {{
            if (window.monaco && window.editor) {{
                window.editor.updateOptions({{ fontSize: {size} }});
                console.log('Font size set to: {size}px');
            }} else {{
                console.log('Editor not ready for font size change');
            }}
        }})();
        """
        self.editorView.evalJS(fontSizeScript)
    
    def setTheme(self, themeName):
        """Set the Monaco editor theme"""
        themeScript = f"""
        (function() {{
            if (window.monaco && window.editor) {{
                monaco.editor.setTheme('{themeName}');
                console.log('Theme set to: {themeName}');
            }} else {{
                console.log('Editor not ready for theme change');
            }}
        }})();
        """
        self.editorView.evalJS(themeScript)

    def setupContextMenu(self):
        """Setup Monaco editor context menu with 'Send to Python Console' option"""
        contextMenuScript = """
        (function() {
            if (!window.editor) {
                console.log('Editor not ready, retrying in 1 second...');
                setTimeout(arguments.callee, 1000);
                return;
            }
            
            // Create a function to get selected text
            window.getSelectedText = function() {
                var selection = window.editor.getSelection();
                if (selection) {
                    return window.editor.getModel().getValueInRange(selection);
                }
                return '';
            };
            
            // Add context menu action to send selected text to Python console
            window.editor.addAction({
                id: 'send-to-python-console',
                label: 'Send Selection to Python Console',
                contextMenuGroupId: 'navigation',
                contextMenuOrder: 1.5,
                keybindings: [
                    monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter
                ],
                run: function(editor) {
                    var selection = editor.getSelection();
                    var selectedText = editor.getModel().getValueInRange(selection);
                    if (selectedText) {
                        window.selectedCodeForExecution = selectedText;
                    }
                    return null;
                }
            });
            console.log('Context menu action registered successfully');
        })();
        """
        self.editorView.evalJS(contextMenuScript)
        
        # Connect to handle the context menu action
        # We'll poll for the selected code when the action is triggered
        self.contextMenuTimer = qt.QTimer()
        self.contextMenuTimer.timeout.connect(self.checkForSelectedCode)
        self.contextMenuTimer.start(100)  # Check every 100ms
    
    def checkForSelectedCode(self):
        """Check if there's selected code to execute from the context menu"""
        self.editorView.evalJS("window.selectedCodeForExecution || ''")
        
    def onNodeSelected(self):
        # Get the selected node
        selectedNode = self.nodeComboBox.currentNode()
        if selectedNode:
            # Ensure storage node is properly configured for .py extension
            self.ensureStorageNodeConfigured(selectedNode)
            
            # Update save location display based on node's storage
            storageNode = selectedNode.GetStorageNode()
            if storageNode and storageNode.GetFileName():
                # Node has an existing file path - show the directory
                existingPath = storageNode.GetFileName()
                directory = os.path.dirname(existingPath)
                self.saveLocationPathEdit.setText(directory)
                self.saveLocationPathEdit.setToolTip(f"Loaded from: {existingPath}")
            elif self.saveLocationPathEdit.text and self.saveLocationPathEdit.text != "No location set (will prompt on save)":
                # Keep the user-selected save location
                pass
            else:
                # No location set
                self.saveLocationPathEdit.setText("")
                self.saveLocationPathEdit.setPlaceholderText("No location set (will prompt on save)")
                self.saveLocationPathEdit.setToolTip("")
            
            self.editorView.setEnabled(True)  # Enable the editor view
            code = selectedNode.GetText()
            self.editorView.evalJS(f"window.editor.getModel().setValue(`{code}`);")
        else:
            self.editorView.setEnabled(False)  # Disable the editor view
            self.editorView.evalJS("window.editor.getModel().setValue('');")  # Clear the editor
    
    def ensureStorageNodeConfigured(self, node):
        """Ensure the storage node is properly configured for .py files"""
        if not isinstance(node, slicer.vtkMRMLTextNode):
            return
        
        storageNode = node.GetStorageNode()
        if not storageNode:
            # Create storage node if it doesn't exist
            storageNode = slicer.vtkMRMLTextStorageNode()
            slicer.mrmlScene.AddNode(storageNode)
            node.SetAndObserveStorageNodeID(storageNode.GetID())
        
        # Configure storage node to use .py extension by default
        if hasattr(storageNode, "SetSupportedReadFileExtensions"):
            storageNode.SetSupportedReadFileExtensions(["py"])
            storageNode.SetSupportedWriteFileExtensions(["py"])
        
        # Set default file extension to .py
        if hasattr(storageNode, "SetDefaultWriteFileExtension"):
            storageNode.SetDefaultWriteFileExtension("py")
        
        # Update the file name if we have a save location set and no existing file
        existingFileName = storageNode.GetFileName()
        if not existingFileName or existingFileName == "":
            # No existing file - set it based on save location
            saveLocation = self.saveLocationPathEdit.text
            if saveLocation and saveLocation != "No location set (will prompt on save)":
                nodeName = node.GetName() if node.GetName() else "Script"
                # Clean the node name for use as filename
                safeName = "".join(c for c in nodeName if c.isalnum() or c in (' ', '_', '-')).strip()
                if not safeName:
                    safeName = "Script"
                newFileName = os.path.join(saveLocation, f"{safeName}.py")
                storageNode.SetFileName(newFileName)

    def onNodeAdded(self, node):
        if isinstance(node, slicer.vtkMRMLTextNode):
            # Configure the storage node for the newly added node
            self.ensureStorageNodeConfigured(node)

    def onEvalResult(self, request, result):
        # Check if this is the result from checking for content changes
        if request == "window.editorContentChanged || false":
            if result == "true":
                # Content has changed - get the current content to update the node
                self.editorView.evalJS("window.editor.getModel().getValue()")
                self._updatingFromChangeDetection = True
                # Reset the flag
                self.editorView.evalJS("window.editorContentChanged = false;")
            self._checkingChanges = False
            return
        
        # Check if this is the result from checking for selected code
        if request == "window.selectedCodeForExecution || ''":
            if result and result.strip() and result != "null" and result != "undefined":
                # We have selected code to execute
                self.executeInPythonConsole(result)
                # Clear the stored selection
                self.editorView.evalJS("window.selectedCodeForExecution = null;")
            return
            
        if request == "window.editor.getModel().getValue()":
            # Check if this is from change detection
            if hasattr(self, '_updatingFromChangeDetection') and self._updatingFromChangeDetection:
                self._updatingFromChangeDetection = False
                # Update the node's text which will mark it as modified
                selectedNode = self.nodeComboBox.currentNode()
                if selectedNode:
                    selectedNode.SetText(result)
                return
    
    def executeInPythonConsole(self, code):
        """Execute selected code directly in Python console"""
        if not code or code == "null":
            print("No code selected to execute.")
            return
        
        print(f"Executing selected code:\n{code}\n")
        try:
            slicer.app.pythonConsole().printOutputMessage(code + "\n")
            slicer.app.pythonManager().executeString(code)
        except Exception as e:
            print(f"Error executing code: {str(e)}")

    def saveEditorContent(self, code):
        selectedNode = self.nodeComboBox.currentNode()
        if selectedNode:
            selectedNode.SetText(code)
            
            # Handle file saving if location is set
            storageNode = selectedNode.GetStorageNode()
            if storageNode:
                existingFileName = storageNode.GetFileName()
                
                if existingFileName:
                    # File was loaded from somewhere - save back to that location
                    success = storageNode.WriteData(selectedNode)
                    if success:
                        print(f"Code saved to: {existingFileName}")
                    else:
                        print(f"Failed to save to: {existingFileName}")
                elif self.saveLocationPathEdit.text and self.saveLocationPathEdit.text != "No location set (will prompt on save)":
                    # Use the user-specified save location
                    saveDir = self.saveLocationPathEdit.text
                    nodeName = selectedNode.GetName() if selectedNode.GetName() else "Script"
                    fileName = os.path.join(saveDir, f"{nodeName}.py")
                    storageNode.SetFileName(fileName)
                    success = storageNode.WriteData(selectedNode)
                    if success:
                        print(f"Code saved to: {fileName}")
                    else:
                        print(f"Failed to save to: {fileName}")
                else:
                    # No location - just save to node
                    print(f"Code saved to node: {selectedNode.GetName()} (no file location set)")
            else:
                print(f"Code saved to node: {selectedNode.GetName()}")
        else:
            print("No node selected to save the code.")

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
