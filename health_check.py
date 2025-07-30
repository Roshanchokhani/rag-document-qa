#!/usr/bin/env python3

import sys
import os
import requests
from pathlib import Path

def check_system_health():
    """Perform system health checks"""
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check if core modules can be imported
    try:
        sys.path.append('src')
        from data_loader import DataLoader
        from text_chunker import TextChunker
        health_status['checks']['imports'] = 'passed'
    except Exception as e:
        health_status['checks']['imports'] = f'failed: {e}'
        health_status['status'] = 'unhealthy'
    
    # Check if data directories exist
    try:
        from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, VECTOR_DB_DIR
        
        dirs_exist = all([
            RAW_DATA_DIR.exists(),
            PROCESSED_DATA_DIR.exists(),
            VECTOR_DB_DIR.exists()
        ])
        
        health_status['checks']['directories'] = 'passed' if dirs_exist else 'failed'
        if not dirs_exist:
            health_status['status'] = 'unhealthy'
            
    except Exception as e:
        health_status['checks']['directories'] = f'failed: {e}'
        health_status['status'] = 'unhealthy'
    
    # Check if HuggingFace API is accessible (optional)
    try:
        response = requests.get('https://huggingface.co', timeout=5)
        health_status['checks']['external_api'] = 'passed' if response.status_code == 200 else 'failed'
    except:
        health_status['checks']['external_api'] = 'failed'
    
    return health_status

if __name__ == "__main__":
    health = check_system_health()
    print(f"System Health: {health['status']}")
    
    for check, result in health['checks'].items():
        status_emoji = "✅" if result == 'passed' else "❌"
        print(f"{status_emoji} {check}: {result}")
    
    # Exit with error code if unhealthy
    sys.exit(0 if health['status'] == 'healthy' else 1)