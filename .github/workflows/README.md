# GitHub Workflows Status

## Current Workflows

### ✅ Active Workflows

#### `basic-checks.yml` - Basic Code Checks
- **Status**: Active and stable
- **Purpose**: Essential code quality validation
- **Triggers**: Push to main/develop branches, PRs
- **Jobs**:
  - Code quality checks (Ruff, Black, MyPy)
  - Basic tests (if requirements.txt exists)
  - Repository health validation

### ⏸️ Disabled Workflows

#### `ci-cd.yml` - Enterprise CI/CD Pipeline (Temporarily Disabled)
- **Status**: Disabled (manual trigger only)
- **Reason**: Resolving deprecation warnings and permission issues
- **Issues Fixed**:
  - CodeQL Action v2 deprecation
  - Upload artifact v3 deprecation
  - Kubernetes security scan SARIF permissions
  - Resource accessibility with integration tokens

## Why This Approach?

The complex enterprise CI/CD pipeline was causing recurring failures due to:

1. **Deprecated GitHub Actions**: Several actions needed version updates
2. **Permission Issues**: Security scanning requires additional repository permissions
3. **Missing Infrastructure**: Some scans expected files not yet in repository
4. **Over-Engineering**: Complex pipeline for current development stage

## Current Solution

- **Stable basic checks** ensure code quality without complexity
- **Graceful error handling** prevents false failure notifications
- **Essential validation** covers linting, formatting, and basic tests
- **Repository health checks** ensure project structure integrity

## Future Plans

The enterprise CI/CD pipeline will be re-enabled when:

1. All infrastructure files are properly configured
2. Repository permissions are set for security scanning
3. Dependencies are fully stabilized
4. Infrastructure deployment is ready for automated testing

## Manual Quality Checks

For now, developers should run local quality checks:

```bash
# Code quality
make lint                  # Ruff + Black + MyPy
make security-scan         # Bandit + Safety  
make test                  # All tests

# Or individual tools
ruff check src/
black --check src/
mypy src/ --ignore-missing-imports
pytest tests/ -v
```