from cx_Freeze import setup, Executable

setup(name =  "LANASE GridFTP File Transfer", version = "1.1.2", description = "LANASE GridFTP File Transfer", executables = [Executable("grid.py")] , )