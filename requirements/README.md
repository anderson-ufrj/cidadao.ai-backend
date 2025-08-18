# Requirements Management

This project uses **pyproject.toml as the single source of truth** for all dependencies. The files in this directory are convenience wrappers.

## ✅ Recommended Installation Methods

### Development Environment
```bash
pip install -e .[dev]
```

### HuggingFace Spaces Deployment  
```bash
pip install -e .[hf]
```

### Production Deployment
```bash
pip install -e .[prod]  
```

### Base Installation Only
```bash
pip install -e .
```

## 📁 File Structure

- **`base.txt`** - References base dependencies from pyproject.toml
- **`dev.txt`** - References development dependencies 
- **`hf.txt`** - References HuggingFace minimal dependencies
- **`production.txt`** - References production dependencies

## 🔧 Maintenance

All dependency management is done in `pyproject.toml`. To update:

1. Edit dependencies in `pyproject.toml`
2. Run `pip install -e .[dev]` to install updated dependencies
3. For HuggingFace deployment, regenerate `requirements.txt`:
   ```bash
   python3 -c "
   import tomllib
   with open('pyproject.toml', 'rb') as f: 
       data = tomllib.load(f)
       deps = data['project']['optional-dependencies']['hf']
       with open('requirements.txt', 'w') as out:
           out.write('# Generated from pyproject.toml[hf]\n\n')
           for dep in deps:
               out.write(dep + '\n')
   "
   ```

## 🎯 Single Source of Truth

- **Primary**: `pyproject.toml` (defines all dependencies)
- **HuggingFace**: `requirements.txt` (generated from pyproject.toml[hf])
- **Convenience**: `requirements/*.txt` (reference pyproject.toml sections)

This approach ensures consistency across all environments and deployment scenarios.