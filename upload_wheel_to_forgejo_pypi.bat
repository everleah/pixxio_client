@echo off
REM Copy local .pypirc to user home, run twine, then remove it
setlocal
set PYPIRC_SRC=%~dp0.pypirc
set PYPIRC_DEST=%USERPROFILE%\.pypirc
copy /Y "%PYPIRC_SRC%" "%PYPIRC_DEST%"
call .venv\Scripts\activate.bat
python -m pip install --upgrade twine
cd /d %~dp0
twine upload -r forgejo dist/*
call .venv\Scripts\deactivate.bat
del "%PYPIRC_DEST%"
endlocal
pause
