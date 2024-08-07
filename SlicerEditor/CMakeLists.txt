#-----------------------------------------------------------------------------
set(MODULE_NAME SlicerEditor)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/UI/${MODULE_NAME}.ui
  )

# Include the monaco-editor folder and its contents
file(GLOB_RECURSE MONACO_EDITOR_RESOURCES RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}/Resources" "Resources/monaco-editor/*")

foreach(file ${MONACO_EDITOR_RESOURCES})
  list(APPEND MODULE_PYTHON_RESOURCES "Resources/${file}")
  message(STATUS "Adding resource: Resources/${file}")
endforeach()

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()