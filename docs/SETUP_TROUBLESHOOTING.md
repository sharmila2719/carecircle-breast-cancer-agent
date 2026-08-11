# Setup Troubleshooting Guide

This document captures common errors encountered during setup and their solutions.

---

## Error 1: `ModuleNotFoundError: No module named 'opentelemetry'`

**When**: Running `from strands import Agent, tool`

**Cause**: `strands-agents` depends on OpenTelemetry packages but they may not install automatically on some systems.

**Solution**:
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-semantic-conventions opentelemetry-instrumentation opentelemetry-instrumentation-threading
```

---

## Error 2: `ModuleNotFoundError: No module named 'opentelemetry.instrumentation.threading'`

**When**: Importing strands after installing base opentelemetry

**Cause**: The threading instrumentation package is a separate install.

**Solution**:
```bash
pip install opentelemetry-instrumentation-threading
```

---

## Error 3: `ModuleNotFoundError: No module named 'docstring_parser'`

**When**: Importing strands tools

**Cause**: `docstring-parser` is a dependency of strands for parsing tool docstrings.

**Solution**:
```bash
pip install docstring-parser
```

---

## Error 4: `ModuleNotFoundError: No module named 'jsonschema'`

**When**: Importing strands experimental features

**Cause**: jsonschema is needed for agent configuration validation.

**Solution**:
```bash
pip install jsonschema
```

---

## Error 5: `ModuleNotFoundError: No module named 'watchdog'`

**When**: Importing strands Agent class

**Cause**: `watchdog` is used for file-watching tool functionality in strands.

**Solution**:
```bash
pip install watchdog
```

---

## Error 6: `ModuleNotFoundError: No module named 'yaml'`

**When**: Importing strands skills module

**Cause**: PyYAML is needed for YAML parsing in skills configuration.

**Solution**:
```bash
pip install pyyaml
```

---

## Error 7: `ModuleNotFoundError: No module named 'plotly'`

**When**: Running the Streamlit dashboard (`streamlit run src/ui/streamlit_app.py`)

**Cause**: Plotly is used for interactive charts in the dashboard but may not have installed correctly during bulk install.

**Solution**:
```bash
pip install plotly pandas
```

---

## Error 8: `ModuleNotFoundError: No module named 'uvicorn'`

**When**: Running `python main.py --mode api`

**Cause**: Uvicorn is the ASGI server for FastAPI.

**Solution**:
```bash
pip install uvicorn fastapi
```

---

## Error 9: `streamlit: command not found` or `not recognized`

**When**: Running `streamlit run ...` directly

**Cause**: On some Windows systems, pip fails to create the executable script due to file permission issues.

**Solution**: Use `python -m streamlit` instead:
```bash
python -m streamlit run src/ui/streamlit_app.py --server.port 8501
```

---

## Error 10: Windows pip `OSError: [WinError 2]` during install

**When**: Running `pip install` on Windows with multiple packages

**Cause**: File locking issue on Windows when pip tries to replace executable scripts.

**Solution**: Install packages one at a time or use `--user` flag:
```bash
pip install --user strands-agents
pip install --user boto3
# etc.
```

---

## Complete One-Shot Fix

If you encounter multiple missing modules, run this single command to install everything:

```bash
pip install strands-agents strands-agents-tools boto3 fastapi uvicorn pydantic python-dotenv jinja2 httpx sqlalchemy alembic aiosqlite python-dateutil apscheduler streamlit plotly pandas opentelemetry-api opentelemetry-sdk opentelemetry-semantic-conventions opentelemetry-instrumentation opentelemetry-instrumentation-threading docstring-parser jsonschema watchdog pyyaml pydantic-settings
```

---

## Verifying Installation

After installation, verify everything works:

```bash
# Test strands-agents
python -c "from strands import Agent, tool; print('strands-agents: OK')"

# Test web dependencies
python -c "import fastapi, uvicorn, streamlit, plotly, pandas; print('web stack: OK')"

# Test database dependencies
python -c "import sqlalchemy, aiosqlite; print('database: OK')"

# Run the demo (no AWS credentials needed)
python main.py --mode demo
```

---

## Running the Application

```bash
# Demo mode (no AWS needed)
python main.py --mode demo

# Streamlit Dashboard
python -m streamlit run src/ui/streamlit_app.py --server.port 8501

# API Server (requires AWS credentials in .env)
python main.py --mode api

# CLI Chat (requires AWS credentials in .env)
python main.py --mode cli
```
