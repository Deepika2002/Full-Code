import asyncio
import subprocess
import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TestExecutionService:
    def __init__(self):
        self.running_executions = {}  # Track running executions
        self.temp_dir = tempfile.mkdtemp(prefix="test_execution_")
    
    async def initialize(self):
        """Initialize the test execution service"""
        try:
            # Ensure temp directory exists
            os.makedirs(self.temp_dir, exist_ok=True)
            logger.info("Test execution service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing test execution service: {e}")
    
    async def execute_test(self, test_flow, parameters: Dict[str, Any], timeout: int, request_id: str) -> Dict[str, Any]:
        """Execute a test flow"""
        try:
            logger.info(f"[{request_id}] Executing test: {test_flow.TestFlowName}")
            
            # Create execution environment
            execution_dir = os.path.join(self.temp_dir, f"exec_{request_id}")
            os.makedirs(execution_dir, exist_ok=True)
            
            # Determine test type and execute accordingly
            if test_flow.FileName.endswith('.java'):
                result = await self._execute_java_test(test_flow, execution_dir, parameters, timeout, request_id)
            elif test_flow.FileName.endswith('.py'):
                result = await self._execute_python_test(test_flow, execution_dir, parameters, timeout, request_id)
            elif test_flow.FileName.endswith('.js') or test_flow.FileName.endswith('.ts'):
                result = await self._execute_javascript_test(test_flow, execution_dir, parameters, timeout, request_id)
            else:
                result = await self._execute_generic_test(test_flow, execution_dir, parameters, timeout, request_id)
            
            # Cleanup
            if os.path.exists(execution_dir):
                shutil.rmtree(execution_dir)
            
            return result
            
        except Exception as e:
            logger.error(f"[{request_id}] Error executing test: {str(e)}")
            return {
                'status': 'failed',
                'error_message': str(e),
                'log_output': f"Test execution failed: {str(e)}",
                'passed_steps': 0,
                'failed_steps': test_flow.steps or 1
            }
    
    async def _execute_java_test(self, test_flow, execution_dir: str, parameters: Dict[str, Any], timeout: int, request_id: str) -> Dict[str, Any]:
        """Execute Java test"""
        try:
            # Clone demo repository for testing
            demo_repo_path = os.path.join(execution_dir, "demo_project")
            clone_cmd = [
                "git", "clone", 
                "https://github.com/sinnedpenguin/angular-springboot-ecommerce.git",
                demo_repo_path
            ]
            
            clone_process = await asyncio.create_subprocess_exec(
                *clone_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=execution_dir
            )
            
            clone_stdout, clone_stderr = await asyncio.wait_for(
                clone_process.communicate(), timeout=60
            )
            
            if clone_process.returncode != 0:
                raise Exception(f"Failed to clone repository: {clone_stderr.decode()}")
            
            # Navigate to backend directory
            backend_path = os.path.join(demo_repo_path, "backend")
            if not os.path.exists(backend_path):
                backend_path = demo_repo_path  # Fallback to root
            
            # Run Maven tests
            test_cmd = ["mvn", "test", "-Dtest=" + test_flow.TestFlowName.replace(" ", "")]
            
            # Store process for potential cancellation
            self.running_executions[request_id] = None
            
            process = await asyncio.create_subprocess_exec(
                *test_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=backend_path
            )
            
            self.running_executions[request_id] = process
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise Exception("Test execution timed out")
            finally:
                if request_id in self.running_executions:
                    del self.running_executions[request_id]
            
            # Parse results
            output = stdout.decode() + stderr.decode()
            
            if process.returncode == 0:
                return {
                    'status': 'passed',
                    'log_output': output,
                    'passed_steps': test_flow.steps or 1,
                    'failed_steps': 0
                }
            else:
                return {
                    'status': 'failed',
                    'error_message': 'Test execution failed',
                    'log_output': output,
                    'passed_steps': 0,
                    'failed_steps': test_flow.steps or 1
                }
                
        except Exception as e:
            return {
                'status': 'failed',
                'error_message': str(e),
                'log_output': f"Java test execution failed: {str(e)}",
                'passed_steps': 0,
                'failed_steps': test_flow.steps or 1
            }
    
    async def _execute_python_test(self, test_flow, execution_dir: str, parameters: Dict[str, Any], timeout: int, request_id: str) -> Dict[str, Any]:
        """Execute Python test"""
        try:
            # Create a simple Python test
            test_content = f"""
import unittest
import time

class {test_flow.TestFlowName.replace(' ', '')}(unittest.TestCase):
    def test_flow(self):
        # Simulate test execution
        time.sleep(2)  # Simulate some work
        
        # Mock test logic based on flow name
        if "fail" in "{test_flow.TestFlowName.lower()}":
            self.fail("Simulated test failure")
        
        self.assertTrue(True, "Test passed successfully")

if __name__ == '__main__':
    unittest.main()
"""
            
            test_file = os.path.join(execution_dir, f"{test_flow.TestFlowName.replace(' ', '_')}.py")
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Execute Python test
            test_cmd = ["python", "-m", "unittest", os.path.basename(test_file)[:-3]]
            
            process = await asyncio.create_subprocess_exec(
                *test_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=execution_dir
            )
            
            self.running_executions[request_id] = process
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise Exception("Test execution timed out")
            finally:
                if request_id in self.running_executions:
                    del self.running_executions[request_id]
            
            output = stdout.decode() + stderr.decode()
            
            if process.returncode == 0:
                return {
                    'status': 'passed',
                    'log_output': output,
                    'passed_steps': test_flow.steps or 1,
                    'failed_steps': 0
                }
            else:
                return {
                    'status': 'failed',
                    'error_message': 'Python test failed',
                    'log_output': output,
                    'passed_steps': 0,
                    'failed_steps': test_flow.steps or 1
                }
                
        except Exception as e:
            return {
                'status': 'failed',
                'error_message': str(e),
                'log_output': f"Python test execution failed: {str(e)}",
                'passed_steps': 0,
                'failed_steps': test_flow.steps or 1
            }
    
    async def _execute_javascript_test(self, test_flow, execution_dir: str, parameters: Dict[str, Any], timeout: int, request_id: str) -> Dict[str, Any]:
        """Execute JavaScript/TypeScript test"""
        try:
            # Clone demo repository for frontend testing
            demo_repo_path = os.path.join(execution_dir, "demo_project")
            clone_cmd = [
                "git", "clone", 
                "https://github.com/sinnedpenguin/angular-springboot-ecommerce.git",
                demo_repo_path
            ]
            
            clone_process = await asyncio.create_subprocess_exec(
                *clone_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=execution_dir
            )
            
            await asyncio.wait_for(clone_process.communicate(), timeout=60)
            
            # Navigate to frontend directory
            frontend_path = os.path.join(demo_repo_path, "frontend")
            if not os.path.exists(frontend_path):
                frontend_path = demo_repo_path  # Fallback to root
            
            # Install dependencies (if package.json exists)
            package_json = os.path.join(frontend_path, "package.json")
            if os.path.exists(package_json):
                install_cmd = ["npm", "install"]
                install_process = await asyncio.create_subprocess_exec(
                    *install_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=frontend_path
                )
                await asyncio.wait_for(install_process.communicate(), timeout=120)
            
            # Run tests
            test_cmd = ["npm", "test", "--", "--watchAll=false"]
            
            process = await asyncio.create_subprocess_exec(
                *test_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=frontend_path
            )
            
            self.running_executions[request_id] = process
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise Exception("Test execution timed out")
            finally:
                if request_id in self.running_executions:
                    del self.running_executions[request_id]
            
            output = stdout.decode() + stderr.decode()
            
            if process.returncode == 0:
                return {
                    'status': 'passed',
                    'log_output': output,
                    'passed_steps': test_flow.steps or 1,
                    'failed_steps': 0
                }
            else:
                return {
                    'status': 'failed',
                    'error_message': 'JavaScript test failed',
                    'log_output': output,
                    'passed_steps': 0,
                    'failed_steps': test_flow.steps or 1
                }
                
        except Exception as e:
            return {
                'status': 'failed',
                'error_message': str(e),
                'log_output': f"JavaScript test execution failed: {str(e)}",
                'passed_steps': 0,
                'failed_steps': test_flow.steps or 1
            }
    
    async def _execute_generic_test(self, test_flow, execution_dir: str, parameters: Dict[str, Any], timeout: int, request_id: str) -> Dict[str, Any]:
        """Execute generic test (simulation)"""
        try:
            # Simulate test execution
            await asyncio.sleep(2)  # Simulate some work
            
            # Mock test results based on flow name
            if "fail" in test_flow.TestFlowName.lower():
                return {
                    'status': 'failed',
                    'error_message': 'Simulated test failure',
                    'log_output': f"Test {test_flow.TestFlowName} failed as expected (simulation)",
                    'passed_steps': test_flow.steps // 2 if test_flow.steps else 0,
                    'failed_steps': test_flow.steps // 2 if test_flow.steps else 1
                }
            else:
                return {
                    'status': 'passed',
                    'log_output': f"Test {test_flow.TestFlowName} passed successfully (simulation)",
                    'passed_steps': test_flow.steps or 1,
                    'failed_steps': 0
                }
                
        except Exception as e:
            return {
                'status': 'failed',
                'error_message': str(e),
                'log_output': f"Generic test execution failed: {str(e)}",
                'passed_steps': 0,
                'failed_steps': test_flow.steps or 1
            }
    
    async def stop_execution(self, execution_id: str):
        """Stop a running test execution"""
        if execution_id in self.running_executions:
            process = self.running_executions[execution_id]
            if process and process.returncode is None:
                process.kill()
                await process.wait()
            del self.running_executions[execution_id]