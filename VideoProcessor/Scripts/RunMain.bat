 
cd /d C:\Users\mabramsR\source\Augment_Workspaces\PhoneSync\

for /f %%a in ('cscript //nologo C:\Users\mabramsR\source\Augment_Workspaces\PhoneSync\VideoProcessor\Scripts\RunMainGetDate.vbs') do set YESTERDAY=%%a
echo %YESTERDAY%

REM C:\Users\mabramsR\source\Augment_Workspaces\PhoneSync\venv\Scripts\python.exe VideoProcessor\Scripts\main.py 
REM C:\Users\mabramsR\source\Augment_Workspaces\PhoneSync\venv\Scripts\python.exe VideoProcessor\Scripts\generate_ai_notes.py 
C:\Users\mabramsR\source\Augment_Workspaces\PhoneSync\venv\Scripts\python.exe VideoProcessor\Scripts\Run_AI_Analysis_Wudan.py --start-date %YESTERDAY%
pause