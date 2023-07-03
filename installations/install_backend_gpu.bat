echo this will recompile llapacpp to use your hardware with gpu enabled. 
pip uninstall llama-cpp-python -y
rem First we need to purge any old installation
pip cache purge
set CMAKE_ARGS=-DLLAMA_CUBLAS=on
set FORCE_CMAKE=1
pip install llama-cpp-python --upgrade