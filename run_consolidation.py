#!/usr/bin/env python3
"""
Quick execution script for file consolidation and SSOT marking
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from consolidate_and_ssot import NexusConsolidationSSOTManager

def main():
    print("🚀 NEXUS Platform - File Consolidation & SSOT Manager")
    print("=" * 60)
    
    try:
        # Initialize manager
        manager = NexusConsolidationSSOTManager()
        
        # Run full process
        print("Starting consolidation and SSOT process...")
        manifest = manager.run_full_consolidation_and_ssot()
        
        print("\n✅ Process completed successfully!")
        print(f"📊 Files consolidated: {sum(len(files) for files in manager.consolidation_report.values())}")
        print(f"🏷️  SSOT files marked: {len(manager.ssot_files)}")
        print(f"🔒 Critical files locked: {len(manager.locked_files)}")
        
        print("\n📋 Check the following files for details:")
        print("- CONSOLIDATION_SSOT_REPORT.md")
        print("- ssot_manifest.json")
        print("- consolidation_ssot.log")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
