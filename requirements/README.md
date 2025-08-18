# Requirements Structure

This directory contains organized dependency files for different environments and use cases.

## File Structure

- **`base.txt`** - Core dependencies needed for all environments
- **`production.txt`** - Full production stack extending base.txt
- **`dev.txt`** - Development tools and testing dependencies
- **`hf.txt`** - HuggingFace Spaces minimal requirements

## Usage

### Development Environment
```bash
pip install -r requirements/dev.txt
```

### Production Environment  
```bash
pip install -r requirements/production.txt
```

### HuggingFace Spaces
```bash
pip install -r requirements/hf.txt
# OR use root requirements.txt (identical to hf.txt)
pip install -r requirements.txt
```

## Primary Source of Truth

The main dependency source is `pyproject.toml`. These requirements files are derived from it for specific deployment scenarios.

## Dependencies Overview

- **Base:** FastAPI, Pydantic, HTTPX, Prometheus, NumPy, Pandas
- **Production:** +Database, +AI/ML, +Security, +Monitoring
- **Development:** +Testing, +Code Quality, +Documentation tools
- **HuggingFace:** Minimal subset for cloud deployment