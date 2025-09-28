#!/usr/bin/env python3
"""
NEXUS Platform - Quick Start Monitoring
Simple script to start monitoring dashboard
"""

import subprocess
import sys
import time
from pathlib import Path

def main():
    """Start the monitoring dashboard"""
    print("🚀 Starting NEXUS Platform Monitoring Dashboard...")
    print("="*60)
    
    # Check if monitoring_dashboard.py exists
    dashboard_file = Path("monitoring_dashboard.py")
    if not dashboard_file.exists():
        print("❌ monitoring_dashboard.py not found!")
        print("Please run this script from the NEXUS root directory.")
        return
    
    try:
        # Start the monitoring dashboard
        print("📊 Launching monitoring dashboard...")
        print("Press Ctrl+C to stop monitoring")
        print("="*60)
        
        # Run the monitoring dashboard
        subprocess.run([sys.executable, "monitoring_dashboard.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting monitoring: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
