call .venv\Scripts\activate.bat
call python setup.py bdist_wheel
call .venv\Scripts\deactivate.bat
pause