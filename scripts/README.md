# 📜 Scripts Directory

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brasil
**Last Updated**: 2025-10-31

## 🎯 Purpose

This directory contains utility scripts for development, deployment, maintenance, and monitoring of the Cidadão.AI backend.

## 📁 Directory Structure

```
scripts/
├── backup/         # Backup and restore utilities
├── database/       # Database management and migrations
├── debug/          # Debugging and analysis tools
├── deployment/     # Deploy to Railway, HF, Docker
├── deprecated/     # Old scripts (to be removed)
├── documentation/  # Doc generation and validation
├── monitoring/     # Grafana, metrics, health checks
├── sql/           # SQL scripts and queries
├── testing/       # Test runners and coverage
└── [root scripts] # Core maintenance utilities
```

## 🛠️ Core Scripts (Root)

### Maintenance & Cleanup
| Script | Purpose | Usage |
|--------|---------|-------|
| `clean_repo.py` | Clean caches, build artifacts, temp files | `python3 scripts/clean_repo.py` |
| `validate_documentation.py` | Validate docs vs actual code | `python3 scripts/validate_documentation.py` |
| `update_agent_line_counts.py` | Update agent line counts in docs | `python3 scripts/update_agent_line_counts.py` |

### Documentation
| Script | Purpose | Usage |
|--------|---------|-------|
| `create_agent_docs.py` | Generate agent documentation | `python3 scripts/create_agent_docs.py` |
| `migrate_docs.py` | Migrate documentation structure | `python3 scripts/migrate_docs.py` |
| `clean_and_restore_docs.py` | Clean and restore docs | `python3 scripts/clean_and_restore_docs.py` |
| `fix_broken_docs.py` | Fix broken documentation links | `python3 scripts/fix_broken_docs.py` |
| `fix_frontmatter.py` | Fix YAML frontmatter in docs | `python3 scripts/fix_frontmatter.py` |

### Security
| Script | Purpose | Usage |
|--------|---------|-------|
| `generate_secrets.py` | Generate secure secrets for .env | `python3 scripts/generate_secrets.py` |

### Deployment
| Script | Purpose | Usage |
|--------|---------|-------|
| `deploy.sh` | Main deployment script | `./scripts/deploy.sh` |
| `deploy_to_hf.sh` | Deploy to HuggingFace Spaces | `./scripts/deploy_to_hf.sh` |
| `deploy_monitoring.sh` | Deploy monitoring stack | `./scripts/deploy_monitoring.sh` |
| `diagnose_railway_env.py` | Diagnose Railway environment | `python3 scripts/diagnose_railway_env.py` |

## 📂 Subdirectories

### 🗄️ backup/
Backup and restore utilities for data and configurations.

### 💾 database/
Database management, migrations, and health checks.
- Schema management
- Migration scripts
- Database optimization

### 🐛 debug/
Debugging tools and diagnostic scripts.
- Performance analysis
- Memory profiling
- Error diagnostics

### 🚀 deployment/
Platform-specific deployment scripts.
- Railway deployment
- Docker configurations
- Cloud platform scripts

### 📊 monitoring/
Monitoring, metrics, and alerting scripts.
- Health checks
- Metrics collection
- Alert configuration
- Performance monitoring

### 🗃️ sql/
SQL scripts for database operations.
- DDL scripts
- DML scripts
- Optimization queries

### 🧪 testing/
Test execution and coverage scripts.
- Unit test runners
- Integration test suites
- Coverage reports

## 🚀 Quick Commands

### Daily Maintenance
```bash
# Clean repository
python3 scripts/clean_repo.py

# Validate documentation
python3 scripts/validate_documentation.py
```

### Development
```bash
# Generate secure secrets
python3 scripts/generate_secrets.py

# Update agent documentation
python3 scripts/update_agent_line_counts.py
```

### Deployment
```bash
# Deploy to production
./scripts/deploy.sh

# Deploy monitoring
./scripts/deploy_monitoring.sh
```

## 📝 Script Naming Convention

- `*.py` - Python scripts (cross-platform)
- `*.sh` - Shell scripts (Unix/Linux)
- `test_*.py` - Test scripts (should be in testing/)
- `fix_*.py` - Fix/repair scripts
- `clean_*.py` - Cleanup scripts
- `deploy_*.sh` - Deployment scripts

## ⚙️ Environment Requirements

### Python Scripts
- Python 3.8+
- Dependencies in requirements.txt
- Virtual environment recommended

### Shell Scripts
- Bash 4.0+
- Unix/Linux environment
- Proper permissions (`chmod +x`)

## 🔒 Security Notes

- Never commit scripts with hardcoded secrets
- Use environment variables for sensitive data
- Scripts should validate inputs
- Follow principle of least privilege

## 📌 Best Practices

1. **Documentation**: Each script should have a header with:
   - Purpose
   - Author (Anderson Henrique da Silva)
   - Date
   - Usage instructions

2. **Error Handling**: All scripts should:
   - Check prerequisites
   - Handle errors gracefully
   - Provide meaningful error messages

3. **Logging**: Important scripts should:
   - Log actions performed
   - Include timestamps
   - Provide verbose options

4. **Testing**: Scripts should be:
   - Tested before deployment
   - Idempotent when possible
   - Safe to run multiple times

## 🆕 Adding New Scripts

When adding new scripts:
1. Place in appropriate subdirectory
2. Add entry to this README
3. Include proper documentation in script
4. Test thoroughly before committing
5. Update permissions if needed

## ⚠️ Deprecated Scripts

Scripts marked for removal:
- Move to `scripts/deprecated/` before deletion
- Document reason for deprecation
- Provide alternative if available

## 📞 Support

**Developer**: Anderson Henrique da Silva
**Email**: andersonhs27@gmail.com
**Location**: Minas Gerais, Brasil

---

*Keep scripts organized, documented, and purposeful!*
