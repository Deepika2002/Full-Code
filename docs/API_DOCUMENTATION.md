# ImpactAnalyzer API Documentation

## Overview

This document provides detailed API specifications for all ImpactAnalyzer microservices.

## Authentication

All endpoints support optional API key authentication via header:

```
X-Impact-Analyzer-Api-Key: your-api-key-here
```

## MS-Index Service (Port 8001)

### POST /index/ingest-graph

Ingest dependency graph from IntelliJ plugin and create vector embeddings.

**Request Body:**
```json
{
  "projectId": "angular-springboot-ecommerce",
  "repoUrl": "https://github.com/sinnedpenguin/angular-springboot-ecommerce.git",
  "commitHash": "main",
  "timestamp": "2025-01-27T12:34:56Z",
  "author": "developer-name",
  "dependencyGraph": {
    "nodes": [
      {
        "id": "UserService",
        "name": "UserService", 
        "type": "class"
      }
    ],
    "edges": [
      {
        "from_node": "UserService",
        "to": "PaymentController",
        "type": "depends-on"
      }
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Dependency graph ingested successfully",
  "indexId": "proj-123_req-456",
  "vectorStorePath": "./vector_store/proj-123_req-456.faiss",
  "metadata": {
    "projectId": "angular-springboot-ecommerce",
    "nodesCount": 15,
    "edgesCount": 23,
    "embeddingsCount": 38
  }
}
```

### POST /index/rebuild-embeddings

Rebuild embeddings for an existing project.

**Request Body:**
```json
{
  "project_id": "angular-springboot-ecommerce"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Embeddings rebuilt successfully",
  "indexId": "proj-123_req-789",
  "vectorStorePath": "./vector_store/proj-123_req-789.faiss",
  "embeddingsCount": 42
}
```

## MS-MR Service (Port 8002)

### POST /mr/analyze

Analyze merge request for impact assessment.

**Request Body:**
```json
{
  "projectId": "angular-springboot-ecommerce",
  "mrId": "MR-456",
  "author": "developer-name",
  "timestamp": "2025-01-27T14:30:00Z",
  "gitDiff": "diff --git a/src/main/java/UserService.java...",
  "changedFiles": [
    {
      "path": "src/main/java/com/ecommerce/service/UserService.java",
      "type": "MODIFY"
    }
  ],
  "repositoryInfo": {
    "repoUrl": "https://github.com/sinnedpenguin/angular-springboot-ecommerce.git",
    "branch": "feature/user-validation",
    "commitHash": "abc123def"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "MR analyzed successfully",
  "analysisId": "analysis-789",
  "mrSummary": {
    "mrId": "MR-456",
    "severityScore": 7.5,
    "affectedClassesCount": 3,
    "testFlowsCount": 2,
    "codeCoverage": 92.1
  },
  "details": {
    "affectedClasses": [
      {
        "name": "UserService",
        "severity": "High",
        "reason": "Core business logic changes"
      }
    ],
    "testFlows": [
      {
        "id": "TF-001",
        "name": "User Registration Flow",
        "priority": "High"
      }
    ],
    "summary": "Analysis of MR affecting 3 classes with high impact on user management"
  }
}
```

### GET /mr/{mr_id}/analysis

Get existing analysis results for a merge request.

**Response:**
```json
{
  "success": true,
  "message": "Analysis retrieved successfully",
  "analysis": {
    "mrId": "MR-456",
    "author": "developer-name",
    "timestamp": "2025-01-27T14:30:00Z",
    "severityScore": 7.5,
    "codeCoverage": 92.1,
    "summary": "High impact changes to user management system",
    "affectedClasses": [
      {
        "name": "UserService",
        "severity": "High", 
        "reason": "Modified core user validation logic"
      }
    ],
    "testFlowIds": ["TF-001", "TF-002"]
  }
}
```

## MS-Common Service (Port 8003)

### GET /stats/yesterday

Get yesterday's project statistics.

**Response:**
```json
{
  "success": true,
  "message": "Yesterday's statistics retrieved successfully",
  "stats": {
    "totalMRs": 23,
    "unitTestCoverage": 87.5,
    "passedTests": 156,
    "failedTests": 8,
    "date": "2025-01-26"
  }
}
```

### GET /stats/current

Get current project statistics.

**Response:**
```json
{
  "success": true,
  "message": "Current statistics retrieved successfully", 
  "stats": {
    "couplingValue": 0.75,
    "totalTestCases": 1250,
    "projectCoverage": 89.2,
    "activeMRs": 7,
    "date": "2025-01-27"
  }
}
```

### GET /impact-map

Get impact analysis data with optional filtering.

**Query Parameters:**
- `mr_id` (optional): Filter by specific MR
- `date_from` (optional): Start date filter (ISO format)
- `date_to` (optional): End date filter (ISO format)

**Response:**
```json
{
  "success": true,
  "message": "Impact map retrieved successfully",
  "impactMap": [
    {
      "mrId": "MR-001",
      "author": "john.doe",
      "timestamp": "2025-01-27T14:30:00Z",
      "severityScore": 7.8,
      "codeCoverage": 92.1,
      "affectedClasses": [
        {
          "name": "UserService",
          "severity": "High",
          "reason": "Core business logic changes"
        }
      ],
      "summary": "High impact changes to user management"
    }
  ],
  "totalMRs": 1
}
```

### GET /dev/code-change-details

Get detailed code change information for a specific MR.

**Query Parameters:**
- `mr_id` (required): MR ID to get details for

**Response:**
```json
{
  "success": true,
  "message": "Code change details retrieved successfully",
  "details": {
    "mrId": "MR-001",
    "author": "john.doe",
    "timestamp": "2025-01-27T14:30:00Z",
    "severityScore": 7.8,
    "codeCoverage": 92.1,
    "affectedClasses": [
      {
        "name": "UserService",
        "severity": "High",
        "reason": "Core business logic changes"
      }
    ],
    "codeChanges": [
      {
        "file": "src/main/java/com/ecommerce/service/UserService.java",
        "changes": "+15 -8",
        "type": "modified",
        "preview": "Added email validation and password encryption logic"
      }
    ],
    "testFlows": [
      {
        "id": "TF-001",
        "name": "User Registration Flow",
        "status": "pending"
      }
    ]
  }
}
```

### GET /test-flows

Get test flows for a specific date.

**Query Parameters:**
- `date` (optional): Date filter (YYYY-MM-DD format)

**Response:**
```json
{
  "success": true,
  "message": "Test flows retrieved successfully",
  "testFlows": [
    {
      "id": "user-registration-flow",
      "name": "User Registration Flow",
      "status": "passed",
      "duration": "2m 34s",
      "lastRun": "14:30",
      "steps": 12,
      "passedSteps": 12,
      "failedSteps": 0
    }
  ],
  "date": "2025-01-27",
  "summary": {
    "total": 5,
    "passed": 2,
    "failed": 1,
    "running": 1,
    "pending": 1
  }
}
```

### POST /test-flow/select

Select a test flow for execution.

**Request Body:**
```json
{
  "testFlowName": "User Registration Flow",
  "mrId": "MR-001",
  "date": "2025-01-27"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test flow selected successfully",
  "selected": true,
  "testFlowName": "User Registration Flow",
  "mrId": "MR-001",
  "date": "2025-01-27",
  "status": "selected_for_execution"
}
```

### GET /code-coverage/impact

Get code coverage impact data.

**Query Parameters:**
- `mr_id` (optional): Filter by specific MR
- `date` (optional): Date filter (YYYY-MM-DD format)

**Response:**
```json
{
  "success": true,
  "message": "Code coverage impact retrieved successfully",
  "coverage": {
    "overallCoverage": 89.2,
    "coverageByModule": {
      "UserService": 94.2,
      "PaymentController": 87.8,
      "OrderEntity": 95.1
    },
    "trend": {
      "lastWeek": 87.1,
      "current": 89.2,
      "change": "+2.1%"
    }
  }
}
```

## MS-AI Service (Port 8004)

### POST /analysis/impact

Generate AI-powered impact analysis.

**Request Body:**
```json
{
  "mrId": "MR-001",
  "changedClasses": ["UserService", "PaymentController"],
  "codeContext": "Modified user service to add email validation and password encryption",
  "vectorContext": {
    "similarClasses": ["AuthService", "ValidationService"],
    "relatedModules": ["Security", "Authentication"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Impact analysis completed successfully",
  "analysis": {
    "affectedClasses": [
      {
        "name": "UserService",
        "severity": "High",
        "reason": "Modified core user validation logic"
      }
    ],
    "severityScore": 7.5,
    "testFlows": [
      {
        "id": "TF-001",
        "name": "User Registration Flow",
        "priority": "High"
      }
    ],
    "codeCoverage": 92.1,
    "summary": "High impact changes requiring comprehensive testing of user management flows"
  }
}
```

### POST /analysis/test-coverage

Analyze test coverage for a specific day.

**Request Body:**
```json
{
  "day": "2025-01-27",
  "allMRs": [
    {
      "mrId": "MR-001",
      "author": "john.doe",
      "changedClasses": ["UserService"],
      "severityScore": 7.5
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test coverage analysis completed successfully",
  "coverageReport": {
    "overallCoverage": 89.2,
    "coverageByModule": {
      "UserService": 92.5,
      "PaymentController": 88.3,
      "OrderEntity": 94.1
    },
    "recommendations": [
      "Increase unit test coverage for payment processing modules",
      "Add integration tests for user registration flow"
    ],
    "riskAreas": [
      {
        "module": "PaymentController",
        "risk": "Medium",
        "reason": "Recent changes may have reduced test coverage"
      }
    ],
    "summary": "Overall coverage at 89.2% with focus needed on payment modules"
  }
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "details": {
    "error": "Detailed error information",
    "requestId": "req-123"
  }
}
```

## HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider implementing rate limiting based on:

- API key
- IP address
- Request type

## Pagination

For endpoints returning large datasets, pagination can be implemented using:

- `limit` - Number of items per page
- `offset` - Number of items to skip
- `page` - Page number

Example:
```
GET /impact-map?limit=10&offset=20
```

## Webhooks

Future versions may support webhooks for:

- MR analysis completion
- Test flow status changes
- Coverage threshold alerts

## SDK and Client Libraries

Consider creating client libraries for:

- Python
- Java
- JavaScript/TypeScript
- IntelliJ Plugin integration