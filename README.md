<img src="./ScriptEditor.png" width=250 alt="ScriptEditor logo">

# ScriptEditor
A simple embedded programming editor for 3D Slicer, based on [monaco editor](https://microsoft.github.io/monaco-editor/).

![Script Editor](screenshot.png) ![Python TextNode](screenshot_2.png)

## Description

The ScriptEditor extension provides the open-source Monaco editor as a module inside the Slicer. It supports auto-completion, and syntax highlighting and allows the scripts to be directly sent to the 3D Slicer's built-in Python console.

## Module Descriptions

- **Script Editor**: This is the only module that the extension provides.

## Typical Use Case

The most typical use case for Script Editor is to develop, debug, and execute Python scripts directly within the 3D Slicer environment. This allows users to automate tasks, create custom analyses, and enhance the functionality of 3D Slicer through scripting.

## Step-by-Step Tutorial

### Step 1: Install ScriptEditor Extension
1. Open 3D Slicer.
2. Go to the `Extension Manager` by clicking on the `View` menu and selecting `Extension Manager`.
3. Search for `ScriptEditor`.
4. Click `Install` next to the `ScriptEditor` extension.
5. Restart 3D Slicer to activate the extension.

### Step 2: Open Script Editor Module
1. After restarting, hit `Ctrl` + `F` (or click the search icon in the toolbar).
2. Select `Script Editor` from the list of modules.

### Step 3: Create or Select a Python Text Node
1. In the `Script Editor` module, you will see a combo box labeled `Script Node`.
2. You can create a new Python text node by selecting "(Create New Python Text Node)" from the combo box.
3. Alternatively, you can select an existing Python text node if you have previously created one.

### Step 4: Writing Python Code
1. Once a text node is selected, the Monaco Editor will be enabled.
2. Write your Python script in the editor. This script can interact with the 3D Slicer API to manipulate data, perform analyses, or automate tasks.

### Step 5: Saving Your Script
1. After writing your script, you can save it by clicking the "Save" button.
2. The script will be saved in the selected text node.

### Step 6: Running Your Script
1. To execute your script, ensure it is selected in the text node combo box.
2. Click the "Run" button (if implemented), or use the Slicer Python Interactor to execute the script manually by copying and pasting the code.

### Step 7: Copying Your Script
1. You can copy the code from the editor to the clipboard by clicking the "Copy" button.
2. This is useful if you want to run the script in the Slicer Python Interactor or share it with others.

## Example Script

Here's an example script that can be used to load a sample volume and apply a Gaussian smoothing filter:

```python
import SampleData
import sitkUtils
import SimpleITK as sitk

# Load sample volume
sampleVolume = SampleData.SampleDataLogic().downloadMRHead()

# Apply Gaussian smoothing
inputImage = sitkUtils.PullVolumeFromSlicer(sampleVolume)
smoothedImage = sitk.SmoothingRecursiveGaussian(inputImage, sigma=2.0)

# Push the result back to Slicer
smoothedVolume = sitkUtils.PushVolumeToSlicer(smoothedImage, name='SmoothedVolume')
slicer.util.setSliceViewerLayers(background=smoothedVolume)
```

## Additional Tips

- **Debugging**: Use `print` statements to output information to the Slicer Python Interactor for debugging purposes.
- **Node Management**: Utilize the Slicer module widgets to manage nodes and visualize results effectively.
- **Resources**: Refer to the [3D Slicer Script Repository](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html) for more script examples and API documentation.

## Previous Versions

The Script Editor extension has undergone significant development and improvements over its versions. A previous iteration of the extension can be found in the repository at [pieper/SlicerEditor](https://github.com/pieper/SlicerEditor).

This project was undertaken during the 3D Slicer Project Week, a collaborative event where developers and researchers work on Slicer-related projects. The specific undertaking for Script Editor was part of the [3D Slicer Project Week 41](https://projectweek.na-mic.org/PW41_2024_MIT/Projects/SimpleEditorForPythonScripting/), held at MIT in 2024. The goal of this project was to create a simple and effective editor for Python scripting within 3D Slicer, leveraging the Monaco Editor for enhanced user experience.

## Funding Acknowledgement

ScriptEditor is created and made available by funding from National Science Foundation (MorphoCloud: DBI/2301405; Imageomics Institute: OAC/2118240) 

