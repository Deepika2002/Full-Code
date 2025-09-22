import openai
import json
from typing import List, Dict, Any, Optional
from ..app import settings

class AIAnalysisService:
    def __init__(self):
        self.client = None
        self.use_openai = False
        
    def initialize(self):
        """Initialize OpenAI client if API key is available"""
        if settings.OPENAI_API_KEY:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                self.client = openai
                self.use_openai = True
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.use_openai = False
        else:
            print("No OpenAI API key provided, using mock AI responses")
            self.use_openai = False
    
    async def analyze_impact(
        self,
        mr_id: str,
        changed_classes: List[str],
        code_context: str,
        vector_context: Optional[Dict[str, Any]],
        request_id: str
    ) -> Dict[str, Any]:
        """Analyze impact of code changes"""
        
        if self.use_openai and self.client:
            return await self._analyze_with_openai(mr_id, changed_classes, code_context, vector_context)
        else:
            return self._create_mock_impact_analysis(mr_id, changed_classes, code_context)
    
    async def analyze_test_coverage(
        self,
        day: str,
        all_mrs: List[Dict[str, Any]],
        request_id: str
    ) -> Dict[str, Any]:
        """Analyze test coverage for a day"""
        
        if self.use_openai and self.client:
            return await self._analyze_coverage_with_openai(day, all_mrs)
        else:
            return self._create_mock_coverage_analysis(day, all_mrs)
    
    async def _analyze_with_openai(
        self,
        mr_id: str,
        changed_classes: List[str],
        code_context: str,
        vector_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze impact using OpenAI"""
        
        prompt = self._build_impact_analysis_prompt(mr_id, changed_classes, code_context, vector_context)
        
        try:
            response = await self.client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect analyzing code impact. Provide structured JSON responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, changed_classes)
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._create_mock_impact_analysis(mr_id, changed_classes, code_context)
    
    async def _analyze_coverage_with_openai(self, day: str, all_mrs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test coverage using OpenAI"""
        
        prompt = self._build_coverage_analysis_prompt(day, all_mrs)
        
        try:
            response = await self.client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in software testing and code coverage analysis. Provide structured JSON responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_coverage_response(ai_response, all_mrs)
            
        except Exception as e:
            print(f"Error calling OpenAI API for coverage analysis: {e}")
            return self._create_mock_coverage_analysis(day, all_mrs)
    
    def _build_impact_analysis_prompt(
        self,
        mr_id: str,
        changed_classes: List[str],
        code_context: str,
        vector_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for impact analysis"""
        
        prompt = f"""
Analyze the impact of the following code changes in merge request {mr_id}:

CHANGED CLASSES:
{', '.join(changed_classes)}

CODE CONTEXT:
{code_context}

VECTOR CONTEXT (if available):
{json.dumps(vector_context, indent=2) if vector_context else 'Not available'}

Please provide a structured analysis in the following JSON format:
{{
    "affectedClasses": [
        {{
            "name": "ClassName",
            "severity": "High|Medium|Low",
            "reason": "Explanation of why this class is affected"
        }}
    ],
    "severityScore": 0.0-10.0,
    "testFlows": [
        {{
            "id": "TF-XXX",
            "name": "Test Flow Name",
            "priority": "High|Medium|Low"
        }}
    ],
    "codeCoverage": 0.0-100.0,
    "summary": "Brief summary of the impact analysis"
}}

Consider:
1. Direct dependencies and transitive dependencies
2. Business logic impact
3. API contract changes
4. Database schema changes
5. Security implications
6. Performance impact

Provide realistic severity scores and coverage estimates based on the changes.
"""
        return prompt
    
    def _build_coverage_analysis_prompt(self, day: str, all_mrs: List[Dict[str, Any]]) -> str:
        """Build prompt for coverage analysis"""
        
        prompt = f"""
Analyze the test coverage impact for day {day} based on the following merge requests:

MERGE REQUESTS:
{json.dumps(all_mrs, indent=2)}

Please provide a structured coverage analysis in the following JSON format:
{{
    "overallCoverage": 0.0-100.0,
    "coverageByModule": {{
        "ModuleName": 0.0-100.0
    }},
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ],
    "riskAreas": [
        {{
            "module": "ModuleName",
            "risk": "High|Medium|Low",
            "reason": "Explanation"
        }}
    ],
    "summary": "Brief summary of coverage analysis"
}}

Consider:
1. Code changes impact on existing tests
2. New code requiring test coverage
3. Critical business logic coverage
4. Integration test requirements
"""
        return prompt
    
    def _parse_ai_response(self, ai_response: str, changed_classes: List[str]) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                return parsed_response
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            # Fallback to mock response
            return self._create_mock_impact_analysis("unknown", changed_classes, "AI parsing failed")
    
    def _parse_coverage_response(self, ai_response: str, all_mrs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse coverage analysis AI response"""
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                return parsed_response
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except Exception as e:
            print(f"Error parsing coverage AI response: {e}")
            return self._create_mock_coverage_analysis("unknown", all_mrs)
    
    def _create_mock_impact_analysis(self, mr_id: str, changed_classes: List[str], code_context: str) -> Dict[str, Any]:
        """Create mock impact analysis"""
        
        # Determine severity based on number of changed classes
        severity_score = min(10.0, len(changed_classes) * 2.5)
        
        # Create affected classes with mock severity
        affected_classes = []
        for i, class_name in enumerate(changed_classes[:5]):  # Limit to 5 classes
            severity = "High" if i == 0 else "Medium" if i < 3 else "Low"
            affected_classes.append({
                "name": class_name,
                "severity": severity,
                "reason": f"Modified in MR {mr_id} - {severity.lower()} impact on dependent modules"
            })
        
        # Create relevant test flows
        test_flows = []
        if any("User" in cls for cls in changed_classes):
            test_flows.append({"id": "TF-001", "name": "User Registration Flow", "priority": "High"})
        if any("Payment" in cls for cls in changed_classes):
            test_flows.append({"id": "TF-002", "name": "Payment Processing Flow", "priority": "High"})
        if any("Order" in cls for cls in changed_classes):
            test_flows.append({"id": "TF-003", "name": "Order Management Flow", "priority": "Medium"})
        
        # Default test flows if none match
        if not test_flows:
            test_flows = [
                {"id": "TF-001", "name": "Core Functionality Flow", "priority": "High"},
                {"id": "TF-002", "name": "Integration Test Flow", "priority": "Medium"}
            ]
        
        # Mock code coverage based on complexity
        code_coverage = max(70.0, min(95.0, 90.0 - len(changed_classes) * 1.5))
        
        return {
            "affectedClasses": affected_classes,
            "severityScore": severity_score,
            "testFlows": test_flows,
            "codeCoverage": code_coverage,
            "summary": f"Impact analysis for MR {mr_id}: {len(changed_classes)} classes modified with severity score {severity_score:.1f}/10. Recommended test coverage: {code_coverage:.1f}%"
        }
    
    def _create_mock_coverage_analysis(self, day: str, all_mrs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create mock coverage analysis"""
        
        mr_count = len(all_mrs)
        base_coverage = 85.0
        
        # Adjust coverage based on MR activity
        overall_coverage = max(70.0, min(95.0, base_coverage - (mr_count * 2)))
        
        return {
            "overallCoverage": overall_coverage,
            "coverageByModule": {
                "UserService": 92.5,
                "PaymentController": 88.3,
                "OrderEntity": 94.1,
                "ProductService": 86.7,
                "CategoryService": 89.2
            },
            "recommendations": [
                "Increase unit test coverage for payment processing modules",
                "Add integration tests for user registration flow",
                "Implement end-to-end tests for order management"
            ],
            "riskAreas": [
                {
                    "module": "PaymentController",
                    "risk": "Medium",
                    "reason": "Recent changes may have reduced test coverage"
                },
                {
                    "module": "UserService",
                    "risk": "Low",
                    "reason": "Well-covered with comprehensive test suite"
                }
            ],
            "summary": f"Coverage analysis for {day}: Overall coverage at {overall_coverage:.1f}% with {mr_count} MRs processed. Focus on payment and user modules."
        }