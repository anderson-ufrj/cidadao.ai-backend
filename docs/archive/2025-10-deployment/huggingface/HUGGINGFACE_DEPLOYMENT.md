# 🤗 HuggingFace Spaces Deployment Guide

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## 📌 Important: Branch Configuration

**HuggingFace Spaces uses the `main` branch only**.

### Current Status (2025-09-25)
- ✅ Using single `main` branch for all deployments
- ✅ All dependencies are properly configured
- ✅ aiofiles, aiosmtplib, and jinja2 are included in requirements.txt

## 🚀 Deployment Instructions

### Deploy to HuggingFace
```bash
# Always use main branch for HuggingFace
git checkout main
git push origin main
git push huggingface main
```

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
1. **Verify requirements.txt has all dependencies**
2. **Clear HuggingFace cache** - Settings → Factory Reboot
3. **Check deployment logs for specific errors**


## 📝 Best Practices

1. **Always test locally first**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

2. **Use pyproject.toml as source of truth**
   - Update dependencies in `pyproject.toml[hf]`
   - Regenerate requirements.txt when needed

3. **Monitor deployment logs** at:
   https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend/logs

## 🎯 Current Configuration

- **Entry point**: `app.py` (default for HuggingFace)
- **Port**: 7860 (HuggingFace standard)
- **Branch**: `main` (HuggingFace default)
- **Python**: 3.11+

Last updated: 2025-09-25
