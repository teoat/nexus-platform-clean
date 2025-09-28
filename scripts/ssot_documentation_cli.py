#!/usr/bin/env python3
"""
NEXUS Platform - SSOT Documentation CLI
Command-line interface for managing SSOT documentation system
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))
from unified_ssot_manager import UnifiedSSOTManager


class SSOTDocumentationCLI:
    """CLI for SSOT Documentation Management"""

    def __init__(self):
        self.ssot_manager = UnifiedSSOTManager()
        self.config_path = Path("config/ssot_documentation_config.yaml")

    def load_config(self) -> Dict[str, Any]:
        """Load SSOT documentation configuration"""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def status(self) -> None:
        """Show documentation status"""
        print("📊 NEXUS Platform - SSOT Documentation Status")
        print("=" * 50)

        doc_status = self.ssot_manager.get_documentation_status()

        for doc_type, status in doc_status.items():
            print(f"\n📁 {doc_type.upper()}")
            print(f"   Current Files: {status['current_count']}/{status['max_files']}")
            print(f"   New Files: {status['new_files']}")
            print(f"   Automation Threshold: {status['automation_threshold']}")
            print(
                f"   Needs Consolidation: {'Yes' if status['needs_consolidation'] else 'No'}"
            )
            print(f"   Files: {', '.join(status['files'])}")

    def add_file(self, file_path: str, doc_type: str, content: str = None) -> None:
        """Add a new documentation file"""
        if not content:
            content = f"# {Path(file_path).stem}\n\nContent added on {datetime.now().isoformat()}"

        result = self.ssot_manager.add_documentation_file(file_path, doc_type, content)

        if result:
            print(f"✅ Successfully added {file_path} as {doc_type} documentation")
        else:
            print(f"❌ Failed to add {file_path}")

    def consolidate(self, doc_type: str) -> None:
        """Trigger consolidation for a documentation type"""
        result = self.ssot_manager.trigger_documentation_consolidation(doc_type)

        if result:
            print(f"✅ Successfully triggered consolidation for {doc_type}")
        else:
            print(f"❌ Failed to trigger consolidation for {doc_type}")

    def intelligent_consolidate_all(self) -> None:
        """Intelligently consolidate all documentation types that exceed limits"""
        print("🧠 Starting intelligent consolidation of all documentation...")
        print("=" * 60)

        results = self.ssot_manager.intelligent_consolidate_all_documentation()

        print("\n📊 **Consolidation Results**")
        print("=" * 40)

        total_consolidated = 0
        total_errors = 0

        for doc_type, result in results.items():
            print(f"\n📁 **{doc_type.upper()}**")

            if result["status"] == "success":
                print(f"   ✅ Status: Successfully consolidated")
                print(f"   📊 Files: {result['files_before']} → {result['files_after']}")
                print(f"   📦 Consolidated: {result['files_consolidated']} files")
                print(f"   📄 Primary File: {result['primary_file']}")
                total_consolidated += result["files_consolidated"]

            elif result["status"] == "error":
                print(f"   ❌ Status: Error")
                print(f"   🔍 Error: {result['error']}")
                print(f"   📊 Files: {result['files_before']} (unchanged)")
                total_errors += 1

            elif result["status"] == "skipped":
                print(f"   ⏭️  Status: Skipped")
                print(f"   📝 Reason: {result['reason']}")
                print(f"   📊 Files: {result['files']}/{result['max_files']}")

        print(f"\n🎯 **Summary**")
        print(f"   📦 Total Files Consolidated: {total_consolidated}")
        print(f"   ❌ Errors: {total_errors}")
        print(
            f"   ✅ Success Rate: {((len(results) - total_errors) / len(results) * 100):.1f}%"
        )

        if total_consolidated > 0:
            print(f"\n💡 **Next Steps**")
            print(f"   - Check the primary files for consolidated content")
            print(f"   - Review archived files in docs/archived/")
            print(f"   - Update any references to the consolidated files")

    def list_types(self) -> None:
        """List all documentation types"""
        print("📋 Available Documentation Types:")
        print("=" * 40)

        config = self.load_config()
        doc_types = config.get("documentation_types", {})

        for doc_type, config in doc_types.items():
            print(f"\n📁 {doc_type}")
            print(f"   Max Files: {config['max_files']}")
            print(f"   Primary File: {config['primary_file']}")
            print(f"   Automation Threshold: {config['automation_threshold']}")

    def validate(self, doc_type: str = None) -> None:
        """Validate documentation"""
        print("🔍 Validating Documentation...")
        print("=" * 40)

        if doc_type:
            # Validate specific type
            doc_status = self.ssot_manager.get_documentation_status()
            if doc_type in doc_status:
                status = doc_status[doc_type]
                print(f"📁 {doc_type.upper()}")
                print(f"   Files: {status['current_count']}/{status['max_files']}")
                print(
                    f"   Status: {'✅ Valid' if not status['needs_consolidation'] else '⚠️ Needs Consolidation'}"
                )
            else:
                print(f"❌ Unknown documentation type: {doc_type}")
        else:
            # Validate all types
            doc_status = self.ssot_manager.get_documentation_status()
            all_valid = True

            for doc_type, status in doc_status.items():
                print(
                    f"📁 {doc_type.upper()}: {'✅ Valid' if not status['needs_consolidation'] else '⚠️ Needs Consolidation'}"
                )
                if status["needs_consolidation"]:
                    all_valid = False

            if all_valid:
                print("\n✅ All documentation types are valid")
            else:
                print("\n⚠️ Some documentation types need consolidation")

    def process_todos(self) -> None:
        """Process TODOs through SSOT manager"""
        print("📝 Processing TODOs...")
        print("=" * 30)

        result = self.ssot_manager.process_todos()

        if "error" in result:
            print(f"❌ Error processing TODOs: {result['error']}")
        else:
            print(f"✅ Processed {result['todos_processed']} TODOs")
            print(f"   Critical: {result['todos_by_priority']['critical']}")
            print(f"   High: {result['todos_by_priority']['high']}")
            print(f"   Medium: {result['todos_by_priority']['medium']}")
            print(f"   Low: {result['todos_by_priority']['low']}")

    def generate_report(self) -> None:
        """Generate comprehensive SSOT report"""
        print("📊 Generating SSOT Report...")
        print("=" * 40)

        report = self.ssot_manager.generate_unified_report()

        # Save report to file
        report_path = Path("reports/ssot_documentation_report.json")
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Report generated: {report_path}")
        print(f"   Timestamp: {report['timestamp']}")
        print(f"   Configurations: {report['status']['configs_managed']}")
        print(f"   TODOs Processed: {report['status']['todos_processed']}")

    def help(self) -> None:
        """Show help information"""
        print("🤖 NEXUS Platform - SSOT Documentation CLI")
        print("=" * 50)
        print("\nAvailable Commands:")
        print("  status              - Show documentation status")
        print("  add <file> <type>   - Add new documentation file")
        print("  consolidate <type>  - Trigger consolidation for type")
        print("  intelligent-consolidate - Intelligently consolidate all types")
        print("  list-types          - List all documentation types")
        print("  validate [type]     - Validate documentation")
        print("  process-todos       - Process TODOs")
        print("  generate-report     - Generate comprehensive report")
        print("  help                - Show this help")
        print("\nDocumentation Types:")
        print("  architecture        - System architecture docs")
        print("  api                 - API documentation")
        print("  deployment          - Deployment and operations")
        print("  development         - Development guides")
        print("  user                - User documentation")
        print("  security            - Security and compliance")
        print("\nExamples:")
        print("  python ssot_documentation_cli.py status")
        print("  python ssot_documentation_cli.py add new_api.md api")
        print("  python ssot_documentation_cli.py consolidate architecture")
        print("  python ssot_documentation_cli.py intelligent-consolidate")
        print("  python ssot_documentation_cli.py validate")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="NEXUS SSOT Documentation CLI")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()

    cli = SSOTDocumentationCLI()

    try:
        if args.command == "status":
            cli.status()
        elif args.command == "add":
            if len(args.args) >= 2:
                cli.add_file(args.args[0], args.args[1])
            else:
                print("❌ Usage: add <file_path> <doc_type>")
        elif args.command == "consolidate":
            if len(args.args) >= 1:
                cli.consolidate(args.args[0])
            else:
                print("❌ Usage: consolidate <doc_type>")
        elif args.command == "intelligent-consolidate":
            cli.intelligent_consolidate_all()
        elif args.command == "list-types":
            cli.list_types()
        elif args.command == "validate":
            doc_type = args.args[0] if args.args else None
            cli.validate(doc_type)
        elif args.command == "process-todos":
            cli.process_todos()
        elif args.command == "generate-report":
            cli.generate_report()
        elif args.command == "help":
            cli.help()
        else:
            print(f"❌ Unknown command: {args.command}")
            cli.help()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
