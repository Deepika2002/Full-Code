import React, { useState } from 'react';
import { useEffect } from 'react';
import { Calendar, CheckCircle, XCircle, Clock, Play, Pause, RotateCcw } from 'lucide-react';
import { apiService } from '../services/api';

const TestsView = () => {
  const [selectedDate, setSelectedDate] = useState('2025-01-27');
  const [selectedFlow, setSelectedFlow] = useState('');
  const [testFlowData, setTestFlowData] = useState<any>({});
  const [testDetails, setTestDetails] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTestFlows = async (date: string) => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await apiService.getTestFlows(date);
        
        setTestFlowData({
          [date]: data.testFlows
        });
        
        // Create mock test details for failed flows
        const mockDetails: any = {};
        data.testFlows.forEach((flow: any) => {
          if (flow.status === 'failed') {
            mockDetails[flow.id] = {
              failureReason: 'Test execution failed',
              errorLog: `Test failed at step ${flow.passedSteps + 1}\nError: Assertion failed\nExpected: success\nActual: failure`,
              affectedComponents: ['TestComponent', 'ServiceLayer', 'DatabaseLayer']
            };
          }
        });
        setTestDetails(mockDetails);
        
      } catch (err) {
        console.error('Error fetching test flows:', err);
        setError('Failed to load test flows. Please check if the backend services are running.');
      } finally {
        setLoading(false);
      }
    };

    fetchTestFlows(selectedDate);
  }, [selectedDate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading test flows...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <XCircle className="w-5 h-5 text-red-500 mr-2" />
          <h3 className="text-red-800 font-medium">Error Loading Test Flows</h3>
        </div>
        <p className="text-red-700 mt-2">{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const currentFlows = testFlowData[selectedDate] || [];
  const summary = {
    total: currentFlows.length,
    passed: currentFlows.filter(f => f.status === 'passed').length,
    failed: currentFlows.filter(f => f.status === 'failed').length,
    running: currentFlows.filter(f => f.status === 'running').length,
    pending: currentFlows.filter(f => f.status === 'pending').length
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
        return <Play className="w-5 h-5 text-blue-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Test Flow Management</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">{summary.total}</p>
            </div>
            <div className="bg-gray-100 p-2 rounded-full">
              <Play className="w-4 h-4 text-gray-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Passed</p>
              <p className="text-2xl font-bold text-green-600">{summary.passed}</p>
            </div>
            <div className="bg-green-100 p-2 rounded-full">
              <CheckCircle className="w-4 h-4 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-2xl font-bold text-red-600">{summary.failed}</p>
            </div>
            <div className="bg-red-100 p-2 rounded-full">
              <XCircle className="w-4 h-4 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running</p>
              <p className="text-2xl font-bold text-blue-600">{summary.running}</p>
            </div>
            <div className="bg-blue-100 p-2 rounded-full">
              <Play className="w-4 h-4 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-yellow-600">{summary.pending}</p>
            </div>
            <div className="bg-yellow-100 p-2 rounded-full">
              <Clock className="w-4 h-4 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Test Flows Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Test Flows for {selectedDate}
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Test Flow
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Run
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Steps
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {currentFlows.map((flow) => (
                <tr key={flow.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(flow.status)}
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">{flow.name}</div>
                        <div className="text-sm text-gray-500">{flow.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(flow.status)}`}>
                      {flow.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {flow.duration}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {flow.lastRun}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                      <span className="text-green-600">{flow.passedSteps}</span>
                      <span className="text-gray-400">/</span>
                      <span className="text-gray-900">{flow.steps}</span>
                      {flow.failedSteps > 0 && (
                        <>
                          <span className="text-gray-400">|</span>
                          <span className="text-red-600">{flow.failedSteps} failed</span>
                        </>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      {flow.status === 'pending' && (
                        <button className="text-blue-600 hover:text-blue-900">
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      {flow.status === 'running' && (
                        <button className="text-yellow-600 hover:text-yellow-900">
                          <Pause className="w-4 h-4" />
                        </button>
                      )}
                      {(flow.status === 'passed' || flow.status === 'failed') && (
                        <button className="text-gray-600 hover:text-gray-900">
                          <RotateCcw className="w-4 h-4" />
                        </button>
                      )}
                      <button 
                        onClick={() => setSelectedFlow(selectedFlow === flow.id ? '' : flow.id)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        Details
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Test Flow Details */}
      {selectedFlow && testDetails[selectedFlow] && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Test Flow Details - {selectedFlow}
            </h3>
            <button 
              onClick={() => setSelectedFlow('')}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Failure Information</h4>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800 mb-2">
                  <strong>Reason:</strong> {testDetails[selectedFlow].failureReason}
                </p>
                <div className="text-sm text-red-700">
                  <strong>Error Log:</strong>
                  <pre className="mt-2 whitespace-pre-wrap font-mono text-xs bg-red-100 p-2 rounded">
                    {testDetails[selectedFlow].errorLog}
                  </pre>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Affected Components</h4>
              <div className="space-y-2">
                {testDetails[selectedFlow].affectedComponents.map((component, index) => (
                  <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                    <XCircle className="w-4 h-4 text-red-500" />
                    <span className="text-sm text-gray-900">{component}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestsView;