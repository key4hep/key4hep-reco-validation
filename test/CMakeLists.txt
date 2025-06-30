#[[
Copyright (c) 2020-2024 Key4hep-Project.

This file is part of Key4hep.
See https://key4hep.github.io/key4hep-doc/ for further info.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
]]


find_package(k4geo REQUIRED)

function(set_test_env testname)
  set_property(TEST ${testname} APPEND PROPERTY ENVIRONMENT "LD_LIBRARY_PATH=${PROJECT_BINARY_DIR}:${PROJECT_BINARY_DIR}/${PROJECT_NAME}:${PROJECT_BINARY_DIR}/${PROJECT_NAME}/genConfDir/${PROJECT_NAME}:${PROJECT_BINARY_DIR}/test/k4FWCoreTest:${PROJECT_BINARY_DIR}/test/k4FWCoreTest/genConfDir/k4FWCoreTest:$<$<TARGET_EXISTS:ROOT::Core>:$<TARGET_FILE_DIR:ROOT::Core>>:$<$<TARGET_EXISTS:EDM4HEP::edm4hep>:$<TARGET_FILE_DIR:EDM4HEP::edm4hep>>:$<$<TARGET_EXISTS:podio::podio>:$<TARGET_FILE_DIR:podio::podio>>:$ENV{LD_LIBRARY_PATH}")
  set_property(TEST ${testname} APPEND PROPERTY ENVIRONMENT "PYTHONPATH=${PROJECT_SOURCE_DIR}/python:${PROJECT_BINARY_DIR}/${PROJECT_NAME}/genConfDir:/${PROJECT_NAME}/genConfDir:$ENV{PYTHONPATH}")
endfunction()

# add_test(NAME "clone_CLDConfig"
#   COMMAND bash -c "git clone https://github.com/key4hep/CLDConfig.git --depth 1 && cp -r CLDConfig/CLDConfig/* . && sed -i -e '/Overlay.Overlay/d' -e '/HighLevelReco.RecoMCTruthLink/d' CLDReconstruction.py"
# )
# set_test_env("clone_CLDConfig")

add_test(NAME "run_ddsim"
  COMMAND bash -c "ddsim --compactFile $K4GEO/FCCee/CLD/compact/CLD_o2_v07/CLD_o2_v07.xml -G --numberOfEvents 3 --outputFile sim.edm4hep.root --gun.energy '10*GeV' --gun.particle 'mu-' --gun.distribution uniform --gun.multiplicity 10"
  )
set_test_env("run_ddsim")

add_test(NAME "modify_ddsim_output"
  COMMAND ${Python3_EXECUTABLE} ${PROJECT_SOURCE_DIR}/scripts/output_editor.py --input-file sim.edm4hep.root --output-file modified_output.root
)
set_test_env("modify_ddsim_output")
set_tests_properties("modify_ddsim_output" PROPERTIES DEPENDS "run_ddsim")

add_test(NAME "run_comparison"
    COMMAND ${Python3_EXECUTABLE} ${PROJECT_SOURCE_DIR}/scripts/compare_sim_outputs.py --new-file modified_output.root --reference-file sim.edm4hep.root -d --modified-output
)
set_test_env("run_comparison")
set_tests_properties("run_comparison" PROPERTIES
    DEPENDS "modify_ddsim_output"
    PASS_REGULAR_EXPRESSION "ComparisonError"
)