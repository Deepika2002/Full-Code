// API service for ImpactAnalyzer frontend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://ms-common-uc.a.run.app';
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-key-123';

const headers = {
  'Content-Type': 'application/json',
  'X-Impact-Analyzer-Api-Key': API_KEY,
};

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'API request failed');
    }

    return data;
  }

  // Yesterday's statistics
  async getYesterdayStats() {
    const response = await this.request<{
      success: boolean;
      stats: {
        totalMRs: number;
        unitTestCoverage: number;
        passedTests: number;
        failedTests: number;
        date: string;
      };
    }>('/stats/yesterday');
    
    return response.stats;
  }

  // Current statistics
  async getCurrentStats() {
    const response = await this.request<{
      success: boolean;
      stats: {
        couplingValue: number;
        totalTestCases: number;
        projectCoverage: number;
        activeMRs: number;
        date: string;
      };
    }>('/stats/current');
    
    return response.stats;
  }

  // Impact map data
  async getImpactMap(filters?: {
    mrId?: string;
    dateFrom?: string;
    dateTo?: string;
  }) {
    let endpoint = '/impact-map';
    const params = new URLSearchParams();
    
    if (filters?.mrId) params.append('mr_id', filters.mrId);
    if (filters?.dateFrom) params.append('date_from', filters.dateFrom);
    if (filters?.dateTo) params.append('date_to', filters.dateTo);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }

    const response = await this.request<{
      success: boolean;
      impactMap: Array<{
        mrId: string;
        author: string;
        timestamp: string;
        severityScore: number;
        codeCoverage: number;
        affectedClasses: Array<{
          name: string;
          severity: string;
          reason: string;
        }>;
        summary: string;
      }>;
      totalMRs: number;
    }>(endpoint);
    
    return response.impactMap;
  }

  // Code change details
  async getCodeChangeDetails(mrId: string) {
    const response = await this.request<{
      success: boolean;
      details: {
        mrId: string;
        author: string;
        timestamp: string;
        severityScore: number;
        codeCoverage: number;
        affectedClasses: Array<{
          name: string;
          severity: string;
          reason: string;
        }>;
        codeChanges: Array<{
          file: string;
          changes: string;
          type: string;
          preview: string;
        }>;
        testFlows: Array<{
          id: string;
          name: string;
          status: string;
        }>;
      };
    }>(`/dev/code-change-details?mr_id=${mrId}`);
    
    return response.details;
  }

  // Test flows
  async getTestFlows(date?: string): Promise<{
    testFlows: Array<{
      id: string;
      name: string;
      status: string;
      duration: string;
      lastRun: string;
      steps: number;
      passedSteps: number;
      failedSteps: number;
    }>;
    summary: {
      total: number;
      passed: number;
      failed: number;
      running: number;
      pending: number;
    };
    date: string;
  }> {
    let endpoint = '/test-flows';
    if (date) {
      endpoint += `?date=${date}`;
    }

    const response = await this.request<{
      success: boolean;
      testFlows: Array<{
        id: string;
        name: string;
        status: string;
        duration: string;
        lastRun: string;
        steps: number;
        passedSteps: number;
        failedSteps: number;
      }>;
      date: string;
      summary: {
        total: number;
        passed: number;
        failed: number;
        running: number;
        pending: number;
      };
    }>(endpoint);
    
    return {
      testFlows: response.testFlows,
      summary: response.summary,
      date: response.date,
    };
  }

  // Select test flow
  async selectTestFlow(testFlowName: string, mrId?: string, date?: string) {
    const response = await this.request<{
      success: boolean;
      selected: boolean;
      testFlowName: string;
      mrId?: string;
      date: string;
      status: string;
    }>('/test-flow/select', {
      method: 'POST',
      body: JSON.stringify({
        testFlowName,
        mrId,
        date,
      }),
    });
    
    return response;
  }

  // Code coverage impact
  async getCodeCoverageImpact(filters?: {
    mrId?: string;
    date?: string;
  }) {
    let endpoint = '/code-coverage/impact';
    const params = new URLSearchParams();
    
    if (filters?.mrId) params.append('mr_id', filters.mrId);
    if (filters?.date) params.append('date', filters.date);
    
    if (params.toString()) {
      endpoint += `?${params.toString()}`;
    }

    const response = await this.request<{
      success: boolean;
      coverage: {
        overallCoverage: number;
        coverageByModule: Record<string, number>;
        trend?: {
          lastWeek: number;
          current: number;
          change: string;
        };
        impactedModules?: Array<{
          module: string;
          coverage: number;
          impact: string;
        }>;
      };
    }>(endpoint);
    
    return response.coverage;
  }

  // Execute test flow
  async executeTestFlow(testFlowId: string, mrId?: string, parameters?: Record<string, any>) {
    const response = await this.request<{
      success: boolean;
      executionId: string;
      status: string;
      testFlowId: string;
      estimatedDuration: string;
    }>('/testcase/execute', {
      method: 'POST',
      body: JSON.stringify({
        TestFlowId: testFlowId,
        mrID: mrId,
        parameters
      }),
    });
    
    return response;
  }

  // Get test execution status
  async getTestExecutionStatus(executionId: string) {
    const response = await this.request<{
      success: boolean;
      executionId: string;
      status: string;
      startTime?: string;
      endTime?: string;
      duration?: number;
      errorMessage?: string;
      gcsLogPath?: string;
      progress?: {
        elapsed_seconds: number;
        estimated_remaining: number;
      };
    }>(`/testcase/status/${executionId}`);
    
    return response;
  }

  // Get test execution logs
  async getTestExecutionLogs(executionId: string) {
    const response = await this.request<{
      success: boolean;
      executionId: string;
      logs: string;
      gcsLogPath?: string;
    }>(`/testcase/logs/${executionId}`);
    
    return response;
  }

  // Health check for debugging
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/common/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService();
export default apiService;