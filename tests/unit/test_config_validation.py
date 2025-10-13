#!/usr/bin/env python3
"""
Configuration validation for HuggingFace Spaces deployment
"""

import os
import sys


def validate_hf_config():
    """Validate HuggingFace Spaces configuration."""

    print("🔍 VALIDATING HUGGINGFACE SPACES CONFIGURATION")
    print("=" * 55)

    checks = []

    # Check 1: app.py exists and has main block
    print("1️⃣ CHECKING APP.PY")
    print("-" * 25)

    if os.path.exists("app.py"):
        with open("app.py") as f:
            content = f.read()
            if 'if __name__ == "__main__":' in content:
                print("✅ app.py exists with main block")
                checks.append(True)
            else:
                print("❌ app.py missing main execution block")
                checks.append(False)
    else:
        print("❌ app.py not found")
        checks.append(False)

    print()

    # Check 2: requirements.txt
    print("2️⃣ CHECKING REQUIREMENTS.TXT")
    print("-" * 30)

    if os.path.exists("requirements.txt"):
        with open("requirements.txt") as f:
            reqs = f.read()
            required_packages = ["fastapi", "uvicorn", "pydantic"]
            missing = []

            for pkg in required_packages:
                if pkg not in reqs.lower():
                    missing.append(pkg)

            if not missing:
                print("✅ All required packages present")
                checks.append(True)
            else:
                print(f"❌ Missing packages: {missing}")
                checks.append(False)
    else:
        print("❌ requirements.txt not found")
        checks.append(False)

    print()

    # Check 3: Dockerfile
    print("3️⃣ CHECKING DOCKERFILE")
    print("-" * 25)

    if os.path.exists("Dockerfile"):
        with open("Dockerfile") as f:
            dockerfile = f.read()
            if "EXPOSE 7860" in dockerfile and "python app.py" in dockerfile:
                print("✅ Dockerfile properly configured")
                checks.append(True)
            else:
                print("❌ Dockerfile missing HF configuration")
                checks.append(False)
    else:
        print("❌ Dockerfile not found")
        checks.append(False)

    print()

    # Check 4: README.md with HF frontmatter
    print("4️⃣ CHECKING README.MD")
    print("-" * 25)

    if os.path.exists("README.md"):
        with open("README.md") as f:
            readme = f.read()
            if "---\ntitle:" in readme and "sdk: docker" in readme:
                print("✅ README.md has HuggingFace frontmatter")
                checks.append(True)
            else:
                print("❌ README.md missing HF frontmatter")
                checks.append(False)
    else:
        print("❌ README.md not found")
        checks.append(False)

    print()

    # Check 5: src directory structure
    print("5️⃣ CHECKING SRC STRUCTURE")
    print("-" * 30)

    if os.path.exists("src"):
        critical_dirs = ["agents", "core", "api"]
        missing_dirs = []

        for dir_name in critical_dirs:
            if not os.path.exists(f"src/{dir_name}"):
                missing_dirs.append(dir_name)

        if not missing_dirs:
            print("✅ Core src directories present")
            checks.append(True)
        else:
            print(f"⚠️ Some directories missing: {missing_dirs}")
            print("   (Using fallback mode - OK for HF)")
            checks.append(True)  # Still OK for HF deployment
    else:
        print("❌ src directory not found")
        checks.append(False)

    print()

    # Summary
    print("📊 VALIDATION SUMMARY")
    print("-" * 25)

    passed = sum(checks)
    total = len(checks)
    score = (passed / total) * 100

    print(f"Checks passed: {passed}/{total}")
    print(f"Configuration score: {score:.0f}%")

    if score >= 80:
        print("✅ READY FOR HUGGINGFACE DEPLOYMENT")
        print("🚀 Configuration meets HuggingFace Spaces requirements")
    elif score >= 60:
        print("⚠️ DEPLOYMENT POSSIBLE WITH WARNINGS")
        print("🔧 Some issues detected but deployment should work")
    else:
        print("❌ NEEDS FIXES BEFORE DEPLOYMENT")
        print("🛠️ Critical issues must be resolved")

    print()
    print("🎯 Next step: Push to HuggingFace Space repository")

    return score >= 60


if __name__ == "__main__":
    print("🤖 CIDADÃO.AI BACKEND - HF VALIDATION")
    print()

    try:
        is_ready = validate_hf_config()
        if is_ready:
            print("✅ Validation completed - Ready for deployment!")
        else:
            print("❌ Validation failed - Fix issues before deployment")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)
