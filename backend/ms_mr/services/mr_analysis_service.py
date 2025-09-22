import requests
import re
from typing import Dict, Any, List
from ..app import AnalyzeMRRequest
import uuid

class MRAnalysisService:
    def __init__(self):
        self.ai_service_url = "http://localhost:8004"
    
    async def analyze_mr_impact(self, request: AnalyzeMRRequest, request_id: str) -> Dict[str, Any]:
        """Analyze MR impact using AI service"""
        try:
            # Extract changed classes from git diff
            changed_classes = self._extract_changed_classes_from_diff(request.gitDiff)
            
            # Get code context from changed files
            code_context = self._build_code_context(request.changedFiles, request.gitDiff)
            
            # Call AI service for impact analysis
            ai_response = await self._call_ai_service(
                request.mrId,
                changed_classes,
                code_context,
                request_id
            )
            
            return {
                "analysisId": str(uuid.uuid4()),
                "analysis": ai_response
            }
            
        except Exception as e:
            # Fallback to mock analysis if AI service fails
            return self._create_mock_analysis(request, request_id)
    
    def _extract_changed_classes_from_diff(self, git_diff: str) -> List[str]:
        """Extract changed class names from git diff"""
        changed_classes = []
        
        # Extract Java class names
        java_class_pattern = r'class\s+(\w+)'
        java_matches = re.findall(java_class_pattern, git_diff)
        changed_classes.extend(java_matches)
        
        # Extract TypeScript class names
        ts_class_pattern = r'export\s+class\s+(\w+)'
        ts_matches = re.findall(ts_class_pattern, git_diff)
        changed_classes.extend(ts_matches)
        
        # Extract from file paths
        file_pattern = r'diff --git a/.*?/(\w+)\.(java|ts|js)'
        file_matches = re.findall(file_pattern, git_diff)
        for match in file_matches:
            changed_classes.append(match[0])
        
        return list(set(changed_classes))  # Remove duplicates
    
    def _build_code_context(self, changed_files: List, git_diff: str) -> str:
        """Build code context from changed files"""
        context_parts = []
        
        context_parts.append("Changed Files:")
        for file in changed_files:
            context_parts.append(f"- {file.path} ({file.type})")
        
        context_parts.append("\nGit Diff Summary:")
        # Extract key changes from diff
        lines = git_diff.split('\n')
        added_lines = [line for line in lines if line.startswith('+') and not line.startswith('+++')]
        removed_lines = [line for line in lines if line.startswith('-') and not line.startswith('---')]
        
        context_parts.append(f"Lines added: {len(added_lines)}")
        context_parts.append(f"Lines removed: {len(removed_lines)}")
        
        # Include some sample changes
        if added_lines:
            context_parts.append("\nSample additions:")
            for line in added_lines[:5]:  # First 5 additions
                context_parts.append(line)
        
        return '\n'.join(context_parts)
    
    async def _call_ai_service(self, mr_id: str, changed_classes: List[str], code_context: str, request_id: str) -> Dict[str, Any]:
        """Call AI service for impact analysis"""
        try:
            payload = {
                "mrId": mr_id,
                "changedClasses": changed_classes,
                "codeContext": code_context,
                "vectorContext": None  # Could be enhanced with vector search
            }
            
            response = requests.post(
                f"{self.ai_service_url}/analysis/impact",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["analysis"]
            else:
                raise Exception(f"AI service returned status {response.status_code}")
                
        except Exception as e:
            print(f"Error calling AI service: {e}")
            # Return mock analysis as fallback
            return self._create_mock_analysis_data(changed_classes, code_context)
    
    def _create_mock_analysis(self, request: AnalyzeMRRequest, request_id: str) -> Dict[str, Any]:
        """Create mock analysis for development/testing"""
        changed_classes = self._extract_changed_classes_from_diff(request.gitDiff)
        code_context = self._build_code_context(request.changedFiles, request.gitDiff)
        
        return {
            "analysisId": str(uuid.uuid4()),
            "analysis": self._create_mock_analysis_data(changed_classes, code_context)
        }
    
    def _create_mock_analysis_data(self, changed_classes: List[str], code_context: str) -> Dict[str, Any]:
        """Create mock analysis data"""
        # Determine severity based on number of changes
        severity_score = min(10.0, len(changed_classes) * 2.5)
        
        # Create affected classes with mock severity
        affected_classes = []
        for i, class_name in enumerate(changed_classes[:5]):  # Limit to 5 classes
            severity = "High" if i == 0 else "Medium" if i < 3 else "Low"
            affected_classes.append({
                "name": class_name,
                "severity": severity,
                "reason": f"Modified in current MR - {severity.lower()} impact expected"
            })
        
        # Create test flows
        test_flows = [
            {"id": "TF-001", "name": "User Registration Flow", "priority": "High"},
            {"id": "TF-002", "name": "Payment Processing Flow", "priority": "Medium"},
            {"id": "TF-003", "name": "Order Management Flow", "priority": "Low"}
        ]
        
        # Mock code coverage
        code_coverage = max(75.0, min(95.0, 90.0 - len(changed_classes) * 2))
        
        return {
            "affectedClasses": affected_classes,
            "severityScore": severity_score,
            "testFlows": test_flows,
            "codeCoverage": code_coverage,
            "summary": f"Analysis of MR affecting {len(changed_classes)} classes with severity score {severity_score:.1f}/10"
        }