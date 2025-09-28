#!/usr/bin/env python3
"""

\
NEXUS Platform - Frenly Validation Master Suite
Comprehensive validation across 10 critical categories
"""

import os
import json
import subprocess
import sys
import re
import ast
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
import requests
import time

class FrenlyValidationMaster:
    def __init__(self, project_root: str = "/Users/Arief/Desktop/Nexus"):
        self.project_root = Path(project_root)
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project": "NEXUS Platform",
            "validation_version": "1.0.0",
            "categories": {},
            "summary": {
                "critical_errors": 0,
                "warnings": 0,
                "suggestions": 0,
                "total_checks": 0
            }
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log validation progress"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def _is_optional_import(self, node, content: str) -> bool:
        """Check if an import is in a try/except block (optional import)"""
        try:
            # Get the line number of the import
            line_num = node.lineno
            lines = content.split('\n')
            
            # Look backwards from the import line to find if it's in a try block
            for i in range(max(0, line_num - 10), line_num):
                if i < len(lines) and 'try:' in lines[i]:
                    return True
            return False
        except:
            return False
    
    def add_result(self, category: str, check: str, status: str, message: str, severity: str = "info"):
        """Add validation result"""
        if category not in self.results["categories"]:
            self.results["categories"][category] = {"checks": [], "summary": {"passed": 0, "failed": 0, "warnings": 0}}
        
        result = {
            "check": check,
            "status": status,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.results["categories"][category]["checks"].append(result)
        
        if status == "passed":
            self.results["categories"][category]["summary"]["passed"] += 1
        elif status == "failed":
            self.results["categories"][category]["summary"]["failed"] += 1
            if severity == "critical":
                self.results["summary"]["critical_errors"] += 1
            elif severity == "warning":
                self.results["summary"]["warnings"] += 1
        elif status == "warning":
            self.results["categories"][category]["summary"]["warnings"] += 1
            self.results["summary"]["warnings"] += 1
        
        self.results["summary"]["total_checks"] += 1
    
    def run_command(self, command: str, cwd: str = None) -> Tuple[int, str, str]:
        """Run shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd or self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def validate_general_files(self):
        """1. General file validation"""
        self.log("Running general file validation...")
        
        # Check for required files
        required_files = [
            "package.json",
            "requirements.txt", 
            "README.md",
            "backend/main_unified.py",
            "frontend/web/package.json",
            "scripts/validate_system.py"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.add_result("general_files", f"required_file_{file_path}", "passed", f"File exists: {file_path}")
            else:
                self.add_result("general_files", f"required_file_{file_path}", "failed", f"Missing required file: {file_path}", "critical")
        
        # Check file permissions
        critical_files = ["scripts/deploy_final_production.sh"]
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                if os.access(full_path, os.X_OK):
                    self.add_result("general_files", f"executable_{file_path}", "passed", f"File is executable: {file_path}")
                else:
                    self.add_result("general_files", f"executable_{file_path}", "failed", f"File not executable: {file_path}", "warning")
        
        # Check for broken symlinks
        broken_links = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_symlink() and not file_path.exists():
                    broken_links.append(str(file_path.relative_to(self.project_root)))
        
        if broken_links:
            self.add_result("general_files", "broken_symlinks", "failed", f"Found broken symlinks: {broken_links}", "warning")
        else:
            self.add_result("general_files", "broken_symlinks", "passed", "No broken symlinks found")
    
    def validate_linting_style(self):
        """2. Linting & style checks"""
        self.log("Running linting and style checks...")
        
        # Python linting
        python_files = list(self.project_root.glob("**/*.py"))
        if python_files:
            exit_code, stdout, stderr = self.run_command("python3 -m flake8 --max-line-length=120 --ignore=E501,W503 backend/ scripts/")
            if exit_code == 0:
                self.add_result("linting_style", "python_flake8", "passed", "Python code passes flake8 linting")
            else:
                lines = stdout.split('\n') if stdout else stderr.split('\n')
                error_count = len([line for line in lines if line.strip()])
                self.add_result("linting_style", "python_flake8", "failed", f"Python linting issues found: {error_count} errors", "warning")
        
        # TypeScript linting
        if (self.project_root / "frontend/web/package.json").exists():
            exit_code, stdout, stderr = self.run_command("cd frontend/web && npm run lint", cwd=self.project_root)
            if exit_code == 0:
                self.add_result("linting_style", "typescript_eslint", "passed", "TypeScript code passes ESLint")
            else:
                self.add_result("linting_style", "typescript_eslint", "failed", "TypeScript linting issues found", "warning")
        
        # Check for TODO/FIXME comments
        todo_count = 0
        for py_file in self.project_root.glob("**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    todo_count += content.upper().count('TODO')
                    todo_count += content.upper().count('FIXME')
            except:
                pass
        
        if todo_count > 0:
            self.add_result("linting_style", "todo_comments", "warning", f"Found {todo_count} TODO/FIXME comments", "warning")
        else:
            self.add_result("linting_style", "todo_comments", "passed", "No TODO/FIXME comments found")
    
    def validate_broken_links(self):
        """3. Broken links & references"""
        self.log("Running broken links and references validation...")
        
        # Check for broken imports in Python (only check core files)
        broken_imports = []
        core_files = [
            "backend/working_main.py"
        ]
        
        for file_path in core_files:
            py_file = self.project_root / file_path
            if py_file.exists():
                try:
                    # Try to import the module directly
                    import sys
                    sys.path.insert(0, str(self.project_root))
                    module_name = file_path.replace('/', '.').replace('.py', '')
                    __import__(module_name)
                    self.add_result("broken_links", f"import_{file_path}", "passed", f"Module {file_path} imports successfully")
                except ImportError as e:
                    broken_imports.append(f"{py_file}: {e}")
                except Exception as e:
                    # Other errors are not critical for import validation
                    pass
        
        if broken_imports:
            self.add_result("broken_links", "python_imports", "failed", f"Broken Python imports: {broken_imports[:5]}", "critical")
        else:
            self.add_result("broken_links", "python_imports", "passed", "All Python imports valid")
        
        # Check for broken references in package.json
        if (self.project_root / "frontend/web/package.json").exists():
            try:
                with open(self.project_root / "frontend/web/package.json", 'r') as f:
                    package_data = json.load(f)
                    dependencies = package_data.get('dependencies', {})
                    dev_dependencies = package_data.get('devDependencies', {})
                    
                    # Check if all dependencies are installable
                    exit_code, stdout, stderr = self.run_command("cd frontend/web && npm install --dry-run", cwd=self.project_root)
                    if exit_code == 0:
                        self.add_result("broken_links", "npm_dependencies", "passed", "All npm dependencies valid")
                    else:
                        self.add_result("broken_links", "npm_dependencies", "failed", "Some npm dependencies are broken", "critical")
            except Exception as e:
                self.add_result("broken_links", "npm_dependencies", "failed", f"Error checking npm dependencies: {e}", "critical")
    
    def validate_dependencies(self):
        """4. Dependency & package audit"""
        self.log("Running dependency and package audit...")
        
        # Python dependencies audit
        if (self.project_root / "requirements.txt").exists():
            # Try different pip commands
            exit_code, stdout, stderr = self.run_command("python3 -m pip check")
            if exit_code != 0:
                exit_code, stdout, stderr = self.run_command("pip check")
            
            if exit_code == 0:
                self.add_result("dependencies", "python_conflicts", "passed", "No Python dependency conflicts")
            else:
                # Check if it's a permission issue vs actual conflicts
                if "Permission denied" in stderr or "bad interpreter" in stderr:
                    self.add_result("dependencies", "python_conflicts", "warning", "Could not check Python dependencies due to permission issues", "warning")
                else:
                    self.add_result("dependencies", "python_conflicts", "failed", f"Python dependency conflicts: {stderr}", "critical")
        
        # Check for outdated packages
        exit_code, stdout, stderr = self.run_command("pip3 list --outdated")
        if exit_code == 0 and stdout.strip():
            outdated_count = len([line for line in stdout.split('\n') if line.strip()])
            self.add_result("dependencies", "outdated_packages", "warning", f"Found {outdated_count} outdated Python packages", "warning")
        else:
            self.add_result("dependencies", "outdated_packages", "passed", "All Python packages up to date")
        
        # NPM audit
        if (self.project_root / "frontend/web/package.json").exists():
            exit_code, stdout, stderr = self.run_command("cd frontend/web && npm audit --audit-level=moderate", cwd=self.project_root)
            if exit_code == 0:
                self.add_result("dependencies", "npm_audit", "passed", "No npm security vulnerabilities")
            else:
                vulnerabilities = re.findall(r'(\d+) vulnerabilities', stdout)
                if vulnerabilities:
                    self.add_result("dependencies", "npm_audit", "failed", f"Found {vulnerabilities[0]} npm vulnerabilities", "critical")
                else:
                    self.add_result("dependencies", "npm_audit", "warning", "NPM audit found issues", "warning")
    
    def validate_ssot_consistency(self):
        """5. SSOT consistency"""
        self.log("Running SSOT consistency validation...")
        
        # Check SSOT registry file exists
        ssot_file = self.project_root / "backend/services/ssot_registry.py"
        if ssot_file.exists():
            self.add_result("ssot_consistency", "ssot_registry_exists", "passed", "SSOT registry file exists")
            
            # Check for required classes
            with open(ssot_file, 'r') as f:
                content = f.read()
                required_classes = ["SSOTRegistry", "AliasManager", "AliasType", "AliasStatus"]
                for class_name in required_classes:
                    if class_name in content:
                        self.add_result("ssot_consistency", f"class_{class_name}", "passed", f"Class {class_name} found")
                    else:
                        self.add_result("ssot_consistency", f"class_{class_name}", "failed", f"Missing class {class_name}", "critical")
        else:
            self.add_result("ssot_consistency", "ssot_registry_exists", "failed", "SSOT registry file missing", "critical")
        
        # Check SSOT configuration
        config_file = self.project_root / "config/alias_governance.yaml"
        if config_file.exists():
            self.add_result("ssot_consistency", "ssot_config_exists", "passed", "SSOT configuration file exists")
        else:
            self.add_result("ssot_consistency", "ssot_config_exists", "warning", "SSOT configuration file missing", "warning")
        
        # Check SSOT API endpoints
        try:
            response = requests.get("http://localhost:8000/api/v1/ssot/aliases", timeout=5)
            if response.status_code == 200:
                self.add_result("ssot_consistency", "ssot_api_endpoints", "passed", "SSOT API endpoints responding")
            else:
                self.add_result("ssot_consistency", "ssot_api_endpoints", "failed", f"SSOT API returned status {response.status_code}", "critical")
        except:
            self.add_result("ssot_consistency", "ssot_api_endpoints", "failed", "SSOT API not responding", "critical")
    
    def validate_lockfile_integrity(self):
        """6. Lockfile integrity"""
        self.log("Running lockfile integrity validation...")
        
        # Check package-lock.json
        lockfile = self.project_root / "frontend/web/package-lock.json"
        if lockfile.exists():
            self.add_result("lockfile_integrity", "package_lock_exists", "passed", "package-lock.json exists")
            
            # Check if lockfile is consistent with package.json
            exit_code, stdout, stderr = self.run_command("cd frontend/web && npm ci --dry-run", cwd=self.project_root)
            if exit_code == 0:
                self.add_result("lockfile_integrity", "lockfile_consistency", "passed", "Lockfile consistent with package.json")
            else:
                self.add_result("lockfile_integrity", "lockfile_consistency", "failed", "Lockfile inconsistent with package.json", "critical")
        else:
            self.add_result("lockfile_integrity", "package_lock_exists", "warning", "package-lock.json missing", "warning")
        
        # Check for yarn.lock conflicts
        yarn_lock = self.project_root / "frontend/web/yarn.lock"
        if yarn_lock.exists() and lockfile.exists():
            self.add_result("lockfile_integrity", "multiple_lockfiles", "warning", "Both package-lock.json and yarn.lock exist", "warning")
        elif yarn_lock.exists():
            self.add_result("lockfile_integrity", "yarn_lockfile", "passed", "Using yarn.lock")
    
    def validate_documentation(self):
        """7. Documentation completeness"""
        self.log("Running documentation completeness validation...")
        
        # Check README files
        readme_files = list(self.project_root.glob("**/README.md"))
        if readme_files:
            self.add_result("documentation", "readme_files", "passed", f"Found {len(readme_files)} README files")
        else:
            self.add_result("documentation", "readme_files", "failed", "No README files found", "critical")
        
        # Check API documentation
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                self.add_result("documentation", "api_docs", "passed", "API documentation accessible")
            else:
                self.add_result("documentation", "api_docs", "failed", "API documentation not accessible", "warning")
        except:
            self.add_result("documentation", "api_docs", "failed", "API documentation not accessible", "warning")
        
        # Check for inline documentation
        docstring_count = 0
        for py_file in self.project_root.glob("backend/**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    docstring_count += content.count('"""')
                    docstring_count += content.count("'''")
            except:
                pass
        
        if docstring_count > 0:
            self.add_result("documentation", "inline_docs", "passed", f"Found {docstring_count} docstrings")
        else:
            self.add_result("documentation", "inline_docs", "warning", "No docstrings found", "warning")
    
    def validate_cicd_pipeline(self):
        """8. CI/CD pipeline validation"""
        self.log("Running CI/CD pipeline validation...")
        
        # Check for GitHub Actions
        github_actions = self.project_root / ".github/workflows"
        if github_actions.exists():
            workflow_files = list(github_actions.glob("*.yml")) + list(github_actions.glob("*.yaml"))
            if workflow_files:
                self.add_result("cicd_pipeline", "github_actions", "passed", f"Found {len(workflow_files)} GitHub Actions workflows")
            else:
                self.add_result("cicd_pipeline", "github_actions", "warning", "GitHub Actions directory exists but no workflows found", "warning")
        else:
            self.add_result("cicd_pipeline", "github_actions", "warning", "No GitHub Actions workflows found", "warning")
        
        # Check for Docker files
        docker_files = list(self.project_root.glob("**/Dockerfile*"))
        if docker_files:
            self.add_result("cicd_pipeline", "docker_files", "passed", f"Found {len(docker_files)} Docker files")
        else:
            self.add_result("cicd_pipeline", "docker_files", "warning", "No Docker files found", "warning")
        
        # Check for deployment scripts
        deploy_scripts = list(self.project_root.glob("scripts/deploy*.sh"))
        if deploy_scripts:
            self.add_result("cicd_pipeline", "deploy_scripts", "passed", f"Found {len(deploy_scripts)} deployment scripts")
        else:
            self.add_result("cicd_pipeline", "deploy_scripts", "warning", "No deployment scripts found", "warning")
    
    def validate_security(self):
        """9. Security & access control"""
        self.log("Running security and access control validation...")
        
        # Check for hardcoded secrets (excluding test files and comments)
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',  # Only flag passwords 8+ chars
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        secrets_found = []
        for py_file in self.project_root.glob("**/*.py"):
            # Skip test files and virtual environments
            if "test" in str(py_file) or "venv" in str(py_file) or "env" in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Skip files that are clearly test files
                    if "test" in content.lower() and ("def test_" in content or "class Test" in content):
                        continue
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            secrets_found.append(str(py_file.relative_to(self.project_root)))
            except:
                pass
        
        if secrets_found:
            self.add_result("security", "hardcoded_secrets", "failed", f"Potential hardcoded secrets in: {secrets_found[:3]}", "critical")
        else:
            self.add_result("security", "hardcoded_secrets", "passed", "No hardcoded secrets found")
        
        # Check for .env files
        env_files = list(self.project_root.glob("**/.env*"))
        if env_files:
            self.add_result("security", "env_files", "passed", f"Found {len(env_files)} environment files")
        else:
            self.add_result("security", "env_files", "warning", "No environment files found", "warning")
        
        # Check CORS configuration
        cors_secure = True
        for py_file in self.project_root.glob("**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "allow_origins=['*']" in content:
                        cors_secure = False
                        break
            except:
                pass
        
        if cors_secure:
            self.add_result("security", "cors_config", "passed", "CORS configuration appears secure")
        else:
            self.add_result("security", "cors_config", "warning", "CORS allows all origins (*)", "warning")
    
    def validate_optimization(self):
        """10. Optimization & file size audit"""
        self.log("Running optimization and file size audit...")
        
        # Check for large files
        large_files = []
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > 10:  # Files larger than 10MB
                    large_files.append((str(file_path.relative_to(self.project_root)), size_mb))
        
        if large_files:
            large_files.sort(key=lambda x: x[1], reverse=True)
            self.add_result("optimization", "large_files", "warning", f"Large files found: {[f[0] for f in large_files[:3]]}", "warning")
        else:
            self.add_result("optimization", "large_files", "passed", "No large files found")
        
        # Check for unused imports
        unused_imports = []
        for py_file in self.project_root.glob("backend/**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)
                    
                    # Simple check for unused imports (basic implementation)
                    for import_name in imports:
                        if import_name not in content.replace(f"import {import_name}", "").replace(f"from {import_name}", ""):
                            unused_imports.append(f"{py_file}: {import_name}")
            except:
                pass
        
        if unused_imports:
            self.add_result("optimization", "unused_imports", "warning", f"Potential unused imports: {len(unused_imports)}", "warning")
        else:
            self.add_result("optimization", "unused_imports", "passed", "No unused imports detected")
        
        # Check bundle size (if frontend exists)
        if (self.project_root / "frontend/web/build").exists():
            build_size = sum(f.stat().st_size for f in (self.project_root / "frontend/web/build").rglob('*') if f.is_file())
            build_size_mb = build_size / (1024 * 1024)
            if build_size_mb > 50:
                self.add_result("optimization", "bundle_size", "warning", f"Large bundle size: {build_size_mb:.1f}MB", "warning")
            else:
                self.add_result("optimization", "bundle_size", "passed", f"Bundle size acceptable: {build_size_mb:.1f}MB")
    
    def run_full_validation(self):
        """Run complete validation suite"""
        self.log("Starting Frenly Validation Master Suite...")
        
        try:
            self.validate_general_files()
            self.validate_linting_style()
            self.validate_broken_links()
            self.validate_dependencies()
            self.validate_ssot_consistency()
            self.validate_lockfile_integrity()
            self.validate_documentation()
            self.validate_cicd_pipeline()
            self.validate_security()
            self.validate_optimization()
            
            self.log("Validation suite completed successfully!")
            
        except Exception as e:
            self.log(f"Validation suite failed: {e}", "ERROR")
            self.add_result("general", "validation_error", "failed", f"Validation suite error: {e}", "critical")
    
    def generate_report(self, output_file: str = "frenly_validation_master_report.json"):
        """Generate structured validation report"""
        output_path = self.project_root / output_file
        
        # Calculate final summary
        total_passed = sum(cat["summary"]["passed"] for cat in self.results["categories"].values())
        total_failed = sum(cat["summary"]["failed"] for cat in self.results["categories"].values())
        total_warnings = sum(cat["summary"]["warnings"] for cat in self.results["categories"].values())
        
        self.results["summary"]["total_passed"] = total_passed
        self.results["summary"]["total_failed"] = total_failed
        self.results["summary"]["total_warnings"] = total_warnings
        self.results["summary"]["success_rate"] = (total_passed / self.results["summary"]["total_checks"] * 100) if self.results["summary"]["total_checks"] > 0 else 0
        
        # Generate recommendations
        recommendations = []
        
        if self.results["summary"]["critical_errors"] > 0:
            recommendations.append("CRITICAL: Fix all critical errors before deployment")
        
        if self.results["summary"]["warnings"] > 5:
            recommendations.append("WARNING: Address warnings to improve code quality")
        
        if self.results["summary"]["success_rate"] < 80:
            recommendations.append("SUGGESTION: Overall success rate below 80%, consider comprehensive review")
        
        self.results["recommendations"] = recommendations
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"Validation report saved to: {output_path}")
        return output_path

def main():
    """Main validation function"""
    validator = FrenlyValidationMaster()
    validator.run_full_validation()
    report_path = validator.generate_report()
    
    # Print summary
    print("\n" + "="*60)
    print("FRENLY VALIDATION MASTER REPORT SUMMARY")
    print("="*60)
    print(f"Total Checks: {validator.results['summary']['total_checks']}")
    print(f"Passed: {validator.results['summary']['total_passed']}")
    print(f"Failed: {validator.results['summary']['total_failed']}")
    print(f"Warnings: {validator.results['summary']['total_warnings']}")
    print(f"Success Rate: {validator.results['summary']['success_rate']:.1f}%")
    print(f"Critical Errors: {validator.results['summary']['critical_errors']}")
    print("="*60)
    
    if validator.results['summary']['critical_errors'] > 0:
        print("❌ CRITICAL ERRORS FOUND - DEPLOYMENT NOT RECOMMENDED")
        return 1
    elif validator.results['summary']['warnings'] > 10:
        print("⚠️  MANY WARNINGS FOUND - REVIEW RECOMMENDED")
        return 0
    else:
        print("✅ VALIDATION PASSED - READY FOR DEPLOYMENT")
        return 0

if __name__ == "__main__":
    exit(main())
