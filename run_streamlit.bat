REM @echo off

REM Switch to D: drive
D:

REM Activate the Conda base environment
call D:\Software\ANACONDA\Scripts\activate base

C:

REM Navigate to the correct directory
cd "C:/Users/mingq/OneDrive - Kansas State University/WildcatHackathon2024"

REM Run the Streamlit app
streamlit run "Home.py"

REM Keep the terminal open after execution
pause
