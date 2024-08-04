cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SlicerEditor)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/SlicerMorph/SlicerEditor")
set(EXTENSION_CONTRIBUTORS "Oshane Thomas (SCRI), Steve Pieper (Isomics, Inc.), Sara Rolfe (SCRI)")
set(EXTENSION_DESCRIPTION "Slicer Editor is a tool for editing and running Python scripts directly within the 3D Slicer interactor environment. It leverages the Monaco Editor for an easier coding experience.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/SlicerMorph/SlicerEditor/main/SlicerEditor.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/SlicerMorph/SlicerEditor/main/screenshot.png https://raw.githubusercontent.com/SlicerMorph/SlicerEditor/main/screenshot_2.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SlicerEditor)
add_subdirectory(PyFile)

## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
