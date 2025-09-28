#!/usr/bin/env python3
"""
Builder Agent
Handles build systems, dependencies, compilation, and runtime issues
"""

import asyncio
import os
import subprocess


class BuilderAgent(BaseAgent):
    """Agent responsible for build systems and dependencies"""

    def __init__(self, agent_id: str = "builder_001"):
        capabilities = AgentCapabilities(
            primary_skills=["build_systems", "dependencies", "compilation", "runtime"],
            secondary_skills=["package_management", "environment_setup", "debugging"],
            collaboration_skills=["integration_testing", "deployment_support"],
        )

        super().__init__(agent_id, "builder", capabilities)
        self.build_history = []
        self.dependency_cache = {}

    async def _work_on_task(self, task: Dict[str, Any]):
        """Work on build-related task"""
        task_id = task.get("id")
        task_type = task.get("type", "build")

        logger.info(f"🔨 Builder Agent working on: {task.get('title')}")

        try:
            if task_type == "build":
                result = await self._handle_build_task(task)
            elif task_type == "dependencies":
                result = await self._handle_dependency_task(task)
            elif task_type == "compilation":
                result = await self._handle_compilation_task(task)
            elif task_type == "runtime":
                result = await self._handle_runtime_task(task)
            else:
                result = await self._handle_generic_task(task)

            await self.complete_task(task_id, result)

        except Exception as e:
            logger.error(f"Builder Agent error: {e}")
            await self.escalate_task(task_id, f"Build error: {str(e)}")

    async def _handle_build_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle build task"""
        project_path = task.get("project_path", ".")
        build_command = task.get("build_command", "npm run build")

        # Update progress
        await self.update_task_progress(task["id"], 0.2, "preparing_build")

        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_path)

        try:
            # Execute build command
            await self.update_task_progress(task["id"], 0.5, "executing_build")

            result = subprocess.run(
                build_command.split(),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            await self.update_task_progress(task["id"], 0.8, "processing_results")

            # Process build results
            build_result = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": build_command,
                "project_path": project_path,
            }

            # Cache build result
            self.build_history.append(
                {
                    "task_id": task["id"],
                    "timestamp": asyncio.get_event_loop().time(),
                    "result": build_result,
                }
            )

            await self.update_task_progress(task["id"], 1.0, "completed")

            return build_result

        finally:
            os.chdir(original_cwd)

    async def _handle_dependency_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dependency management task"""
        action = task.get("action", "install")
        package_manager = task.get("package_manager", "npm")

        await self.update_task_progress(task["id"], 0.3, "analyzing_dependencies")

        if action == "install":
            result = await self._install_dependencies(package_manager)
        elif action == "update":
            result = await self._update_dependencies(package_manager)
        elif action == "audit":
            result = await self._audit_dependencies(package_manager)
        else:
            result = {"error": f"Unknown dependency action: {action}"}

        await self.update_task_progress(task["id"], 1.0, "completed")
        return result

    async def _install_dependencies(self, package_manager: str) -> Dict[str, Any]:
        """Install dependencies"""
        if package_manager == "npm":
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
        elif package_manager == "pip":
            result = subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
            )
        else:
            return {"error": f"Unsupported package manager: {package_manager}"}

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "package_manager": package_manager,
        }

    async def _update_dependencies(self, package_manager: str) -> Dict[str, Any]:
        """Update dependencies"""
        if package_manager == "npm":
            result = subprocess.run(["npm", "update"], capture_output=True, text=True)
        elif package_manager == "pip":
            result = subprocess.run(
                ["pip", "install", "--upgrade", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
            )
        else:
            return {"error": f"Unsupported package manager: {package_manager}"}

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "package_manager": package_manager,
        }

    async def _audit_dependencies(self, package_manager: str) -> Dict[str, Any]:
        """Audit dependencies for vulnerabilities"""
        if package_manager == "npm":
            result = subprocess.run(["npm", "audit"], capture_output=True, text=True)
        elif package_manager == "pip":
            result = subprocess.run(["pip", "check"], capture_output=True, text=True)
        else:
            return {"error": f"Unsupported package manager: {package_manager}"}

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "package_manager": package_manager,
            "vulnerabilities_found": "vulnerabilities" in result.stdout.lower(),
        }

    async def _handle_compilation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle compilation task"""
        source_files = task.get("source_files", [])
        output_path = task.get("output_path", "./dist")
        compiler = task.get("compiler", "typescript")

        await self.update_task_progress(task["id"], 0.2, "preparing_compilation")

        if compiler == "typescript":
            result = await self._compile_typescript(source_files, output_path)
        elif compiler == "webpack":
            result = await self._compile_webpack(source_files, output_path)
        else:
            result = {"error": f"Unsupported compiler: {compiler}"}

        await self.update_task_progress(task["id"], 1.0, "completed")
        return result

    async def _compile_typescript(
        self, source_files: list, output_path: str
    ) -> Dict[str, Any]:
        """Compile TypeScript files"""
        result = subprocess.run(
            ["npx", "tsc", "--outDir", output_path], capture_output=True, text=True
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "compiler": "typescript",
            "output_path": output_path,
        }

    async def _compile_webpack(
        self, source_files: list, output_path: str
    ) -> Dict[str, Any]:
        """Compile with Webpack"""
        result = subprocess.run(
            ["npx", "webpack", "--output-path", output_path],
            capture_output=True,
            text=True,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "compiler": "webpack",
            "output_path": output_path,
        }

    async def _handle_runtime_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle runtime task"""
        runtime_command = task.get("runtime_command", "npm start")
        port = task.get("port", 3000)

        await self.update_task_progress(task["id"], 0.3, "starting_runtime")

        # Start runtime process
        process = subprocess.Popen(
            runtime_command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait a bit to see if it starts successfully
        await asyncio.sleep(2)

        if process.poll() is None:
            # Process is running
            await self.update_task_progress(task["id"], 0.8, "runtime_started")

            return {
                "success": True,
                "pid": process.pid,
                "command": runtime_command,
                "port": port,
                "status": "running",
            }
        else:
            # Process failed to start
            stdout, stderr = process.communicate()
            return {
                "success": False,
                "stdout": stdout,
                "stderr": stderr,
                "command": runtime_command,
                "return_code": process.returncode,
            }

    async def _handle_generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic build task"""
        command = task.get("command", "echo 'No command specified'")

        result = subprocess.run(
            command.split(), capture_output=True, text=True, timeout=60
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command,
            "return_code": result.returncode,
        }

    async def _perform_peer_review(
        self, task_id: str, review_data: Any
    ) -> Dict[str, Any]:
        """Perform peer review for build tasks"""
        # Review build outputs for common issues
        issues = []
        recommendations = []

        if isinstance(review_data, dict):
            if not review_data.get("success", False):
                issues.append("Build failed")
                recommendations.append("Check build logs for errors")

            if review_data.get("stderr"):
                issues.append("Build warnings present")
                recommendations.append("Review and fix warnings")

            if "error" in review_data.get("stdout", "").lower():
                issues.append("Runtime errors detected")
                recommendations.append("Test application functionality")

        return {
            "reviewer": self.agent_id,
            "issues_found": len(issues),
            "issues": issues,
            "recommendations": recommendations,
            "overall_quality": "good" if len(issues) == 0 else "needs_improvement",
        }

    async def _execute_gemini_cli(self, command: str) -> Dict[str, Any]:
        """Execute Gemini CLI for build-related commands"""
        # Enhanced Gemini CLI execution for build tasks
        if "build" in command.lower():
            # Use Gemini CLI to analyze build issues
            enhanced_command = f"gemini analyze-build --command '{command}'"
        elif "dependencies" in command.lower():
            # Use Gemini CLI to analyze dependency issues
            enhanced_command = f"gemini analyze-dependencies --command '{command}'"
        else:
            enhanced_command = f"gemini {command}"

        # Simulate enhanced execution
        return {
            "success": True,
            "output": f"Enhanced build analysis: {enhanced_command}",
            "command": enhanced_command,
            "enhanced": True,
        }
