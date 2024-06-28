cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SlicerEditor)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/SlicerEditor")
set(EXTENSION_CONTRIBUTORS "Oshane Thomas (SCRI), Steve Pieper (Isomics, Inc.), Sara Rolfe (SCRI)")
set(EXTENSION_DESCRIPTION "Slicer Editor is a robust tool for python editing and running Python scripts directly within the 3D Slicer interactor environment. It leverages the Monaco Editor for an advanced coding experience, seamlessly integrating with Slicer’s API to streamline medical image computing workflows.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/SlicerEditor.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/SlicerEditor/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SlicerEditor)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
