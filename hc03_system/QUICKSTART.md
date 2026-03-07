# HC-03 System - Quick Start Guide for VS Code

## ⚡ 5-Minute Quick Start

### Step 1: Open Terminal in VS Code

Press `Ctrl + `` to open the integrated terminal.

### Step 2: Navigate to Project Directory

```bash
cd hc03_system
```

### Step 3: Create Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run Tests

```bash
python test_runner.py
```

This will test all modules and generate sample reports.

### Step 7: Start the API Server

```bash
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 8: Open in Browser

Visit: **http://127.0.0.1:8000/docs**

You'll see the interactive API documentation!

---

## 🔧 VS Code Setup (Optional but Recommended)

### 1. Install Recommended Extensions

In VS Code Extension Marketplace, install:
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **FastAPI** (Pex Ecstatic)
- **Thunder Client** or **REST Client** (for API testing)

### 2. Create Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "HC-03 FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/hc03_system"
    }
  ]
}
```

### 3. Create Debug Configuration

Now press `F5` to start debugging the API server!

---

## 📡 Testing APIs in VS Code

### Using Thunder Client

1. Install Thunder Client extension
2. Click Thunder Client icon on left sidebar
3. Click "New Request"
4. Set URL: `http://127.0.0.1:8000/health`
5. Click Send

### Using REST Client Extension

Create file `test.http`:

```http
### Health Check
GET http://127.0.0.1:8000/health

### Explain Interaction
POST http://127.0.0.1:8000/explain-interaction
Content-Type: application/json

{
  "drug_1": "Warfarin",
  "drug_2": "Aspirin",
  "severity": "High",
  "clinical_risk": "Increased bleeding risk"
}

### Generate Report
POST http://127.0.0.1:8000/generate-report
Content-Type: application/json

{
  "patient_data": {
    "patient_id": "P102",
    "age": 72,
    "medications": ["Warfarin", "Aspirin", "Ibuprofen"],
    "interactions": [
      {
        "drug_1": "Warfarin",
        "drug_2": "Aspirin",
        "severity": "High",
        "clinical_risk": "Increased bleeding risk"
      }
    ]
  },
  "output_format": "json"
}
```

Then click "Send Request" on any request!

---

## 📝 Running Individual Tests

### Test AI Explanation Engine Only

```bash
python -c "from modules.ai_explanation_engine import AIExplanationEngine; engine = AIExplanationEngine(); print(engine.generate_explanation('Warfarin', 'Aspirin', 'High', 'Increased bleeding risk'))"
```

### Test Report Generator

```python
python -c "
from modules.report_generator import ReportGenerator
import json

generator = ReportGenerator()
data = {
    'patient_id': 'P102',
    'age': 72,
    'medications': ['Warfarin', 'Aspirin'],
    'interactions': [{
        'drug_1': 'Warfarin',
        'drug_2': 'Aspirin',
        'severity': 'High',
        'clinical_risk': 'Bleeding risk'
    }]
}
report = generator.generate_report(data)
print(json.dumps(report, indent=2))
"
```

---

## 🛑 Troubleshooting in VS Code

### Problem: "Python not found"

**Solution:**
1. Open Command Palette: `Ctrl + Shift + P`
2. Type: "Python: Select Interpreter"
3. Choose the Python version you installed

### Problem: "Module not found"

**Solution:**
1. Ensure virtual environment is activated (see "(venv)" in terminal)
2. Run: `pip install -r requirements.txt`

### Problem: "Port 8000 already in use"

**Solution:** Change port in `config.py`:
```python
FASTAPI_PORT = 8001  # or any free port
```

### Problem: "API server won't start"

**Solution:**
1. Check logs in `hc03_system.log`
2. Verify all dependencies: `pip list`
3. Try: `uvicorn app:app --host 127.0.0.1 --port 8000`

---

## 📊 Project File Structure in VS Code

Click the Explorer icon (Ctrl + B) to see:

```
📁 hc03_system
  ├── 📄 app.py                 ← Main FastAPI app
  ├── 📄 config.py              ← Configuration
  ├── 📄 test_runner.py         ← Run tests
  ├── 📄 requirements.txt
  ├── 📄 README.md
  ├── 📄 .env.example
  ├── 📁 modules
  │   ├── report_generator.py
  │   └── ai_explanation_engine.py
  ├── 📁 utils
  │   ├── formatter.py
  │   └── pdf_exporter.py
  └── 📁 data
      └── sample_interaction.json
```

---

## 🚀 Next Steps

1. **Read the API docs**: Visit `http://127.0.0.1:8000/docs`
2. **Review examples**: Check `README.md` for response examples
3. **Try the API**: Use Thunder Client or REST Client
4. **Modify data**: Edit `data/sample_interaction.json`
5. **Customize**: Update `config.py` for your needs
6. **Integrate**: Use the modules in your own application

---

## 💡 Pro Tips

**Tip 1:** Keep two terminals:
- Terminal 1: API server (`python app.py`)
- Terminal 2: Testing/development

**Tip 2:** Set VS Code to detect changes automatically:
Go to Settings → Files: Auto Save → "afterDelay"

**Tip 3:** Use Python syntax highlighting smartly:
In `config.py`, type `OPENAI_API_KEY` and VS Code will remember it!

**Tip 4:** Run tests frequently:
```bash
python test_runner.py
```

---

## 📚 Key Files to Edit

| File | Purpose |
|------|---------|
| `config.py` | Change API key, ports, settings |
| `modules/ai_explanation_engine.py` | Customize AI explanations |
| `modules/report_generator.py` | Modify report structure |
| `data/sample_interaction.json` | Add test data |
| `app.py` | Add new endpoints |

---

## ✅ Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests pass (`python test_runner.py`)
- [ ] API server running (`python app.py`)
- [ ] Can access `http://127.0.0.1:8000/docs`
- [ ] Can make API calls successfully
- [ ] Reports are generated correctly

---

## 🤔 Questions?

1. **Check README.md** for detailed documentation
2. **Review test_runner.py** for usage examples
3. **Read docstrings** in Python files (Ctrl + K, Ctrl + I in VS Code)
4. **Check logs** in `hc03_system.log`
5. **Try the interactive docs** at `/docs` endpoint

---

**Happy coding! 🎉**
