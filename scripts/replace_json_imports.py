#!/usr/bin/env python3
"""
Script to replace all direct json imports with json_utils
"""

import os
import re
from pathlib import Path

def replace_json_imports(file_path):
    """Replace json imports and usage in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace import statements
        content = re.sub(r'^import json\s*$', 'from src.core import json_utils', content, flags=re.MULTILINE)
        content = re.sub(r'^from json import (.+)$', r'from src.core.json_utils import \1', content, flags=re.MULTILINE)
        
        # Replace json. usage
        content = re.sub(r'\bjson\.', 'json_utils.', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all Python files that import json."""
    src_dir = Path(__file__).parent.parent / 'src'
    
    # Files to process
    files_to_process = [
        'core/audit.py',
        'core/secret_manager.py',
        'infrastructure/monitoring_service.py',
        'infrastructure/messaging/queue_service.py',
        'infrastructure/observability/structured_logging.py',
        'infrastructure/agent_pool.py',
        'infrastructure/health/dependency_checker.py',
        'infrastructure/apm/integrations.py',
        'infrastructure/database.py',
        'infrastructure/cache_system.py',
        'api/models/pagination.py',
        'api/routes/reports.py',
        'api/routes/websocket_chat.py',
        'api/routes/analysis.py',
        'api/routes/investigations.py',
        'api/routes/chat_emergency.py',
        'api/routes/chat_simple.py',
        'api/routes/websocket.py',
        'api/websocket.py',
        'agents/drummond.py',
        'agents/nana.py',
        'agents/niemeyer.py',
        'agents/lampiao.py',
        'tools/api_test.py',
        'tools/ai_analyzer.py',
        'tools/data_visualizer.py',
        'tools/data_integrator.py',
        'services/rate_limit_service.py',
        'services/cache_service.py',
        'services/chat_service.py',
        'services/maritaca_client.py',
        'ml/data_pipeline.py',
        'ml/model_api.py',
        'ml/advanced_pipeline.py',
        'ml/hf_cidadao_model.py',
        'ml/cidadao_model.py',
        'ml/transparency_benchmark.py',
        'ml/hf_integration.py',
        'ml/training_pipeline.py',
    ]
    
    processed = 0
    for file_path in files_to_process:
        full_path = src_dir / file_path
        if full_path.exists():
            if replace_json_imports(full_path):
                print(f"✓ Updated: {file_path}")
                processed += 1
            else:
                print(f"- Skipped: {file_path} (no changes)")
        else:
            print(f"✗ Not found: {file_path}")
    
    print(f"\nProcessed {processed} files")

if __name__ == "__main__":
    main()