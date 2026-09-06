# Attendance2Sheet

## Instructions
Create virtual environment and install dependencies
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Add Gemini API key
```powershell
$env:GEMINI_API_KEY = "your api key here"
```

Run the application
```powershell
# activate the environment if not already activated
.venv\Scripts\Activate.ps1

# run the streamlit app
streamlit run main.py
```