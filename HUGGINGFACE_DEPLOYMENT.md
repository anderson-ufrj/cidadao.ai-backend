# 🤗 HuggingFace Spaces Deployment Guide

## 📌 Important: Branch Configuration

**HuggingFace Spaces uses the `main` branch by default**, not `hf-fastapi`.

### Current Status (2025-09-24)
- ✅ Both `main` and `hf-fastapi` branches are synchronized
- ✅ All dependencies are properly configured
- ✅ aiofiles, aiosmtplib, and jinja2 are included in requirements.txt

## 🚀 Deployment Instructions

### Option 1: Keep using main branch (Recommended)
```bash
# Always deploy to main branch for HuggingFace
git checkout main
git merge hf-fastapi  # If you have changes in hf-fastapi
git push origin main
git push huggingface main
```

### Option 2: Configure HuggingFace to use hf-fastapi
1. Go to: https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend/settings
2. Look for "Repository Settings" or "Branch Settings"
3. Change default branch from `main` to `hf-fastapi`

## 📋 Required Dependencies

The following must be in `requirements.txt` for HuggingFace deployment:
```
aiofiles>=23.2.1        # For async file operations in audit.py
aiosmtplib>=3.0.1       # For email notifications
jinja2>=3.1.3           # For email templates
email-validator>=2.0.0   # For email validation
```

## 🔧 Troubleshooting

### Module Import Errors
1. **Check which branch HuggingFace is using** - it's usually `main`
2. **Verify requirements.txt has all dependencies** in that branch
3. **Clear HuggingFace cache** - Settings → Factory Reboot

### Sync Branches
```bash
# To sync hf-fastapi changes to main
git checkout main
git merge hf-fastapi
git push origin main
git push huggingface main

# To sync main changes to hf-fastapi
git checkout hf-fastapi
git merge main
git push origin hf-fastapi
git push huggingface hf-fastapi
```

## 📝 Best Practices

1. **Always test locally first**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

2. **Keep both branches synchronized** to avoid confusion

3. **Use pyproject.toml as source of truth**
   - Update dependencies in `pyproject.toml[hf]`
   - Regenerate requirements.txt when needed

4. **Monitor deployment logs** at:
   https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend/logs

## 🎯 Current Configuration

- **Entry point**: `app.py` (default for HuggingFace)
- **Port**: 7860 (HuggingFace standard)
- **Branch**: `main` (HuggingFace default)
- **Python**: 3.11+

Last updated: 2025-09-24 23:36:00