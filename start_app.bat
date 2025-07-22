@echo off
echo Starting LinkedIn Scraper Suite...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo Installing/updating requirements...
pip install -r requirements.txt
echo.

REM Start Final Streamlit app
echo Starting Final LinkedIn Scraper application...
echo Open your browser to: http://localhost:8501
echo.
streamlit run final_streamlit_app.py

pause
