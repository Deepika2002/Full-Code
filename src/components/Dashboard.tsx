import React from 'react';
import { TrendingUp, GitMerge, TestTube, Activity, AlertTriangle, CheckCircle } from 'lucide-react';

const Dashboard = () => {
  const yesterdayStats = {
    totalMRs: 23,
    unitTestCoverage: 87.5,
    passedTests: 156,
    failedTests: 8
  };

  const currentStats = {
    couplingValue: 0.73,
    totalTestCases: 1247,
    projectCoverage: 89.2,
    activeMRs: 7
  };

  const recentMRs = [
    {
      id: 'MR-001',
      author: 'john.doe',
      timestamp: '2025-01-27 14:30',
      coverage: 92.1,
      severity: 'Medium',
      changedClasses: ['UserService', 'PaymentController', 'OrderEntity']
    },
    {
      id: 'MR-002',
      author: 'jane.smith',
      timestamp: '2025-01-27 13:15',
      coverage: 85.7,
      severity: 'Low',
      changedClasses: ['ProductRepository', 'CategoryService']
    },
    {
      id: 'MR-003',
      author: 'mike.wilson',
      timestamp: '2025-01-27 11:45',
      coverage: 78.3,
      severity: 'High',
      changedClasses: ['SecurityConfig', 'AuthenticationFilter', 'JwtUtil']
    }
  ];

  return (
    <div className="space-y-8">
      {/* Yesterday Statistics */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Yesterday's Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total MRs</p>
                <p className="text-3xl font-bold text-gray-900">{yesterdayStats.totalMRs}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <GitMerge className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+12% from last week</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Unit Test Coverage</p>
                <p className="text-3xl font-bold text-gray-900">{yesterdayStats.unitTestCoverage}%</p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <TestTube className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: `${yesterdayStats.unitTestCoverage}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tests Passed</p>
                <p className="text-3xl font-bold text-green-600">{yesterdayStats.passedTests}</p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tests Failed</p>
                <p className="text-3xl font-bold text-red-600">{yesterdayStats.failedTests}</p>
              </div>
              <div className="bg-red-100 p-3 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Current Statistics */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Current Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Coupling Value</p>
                <p className="text-3xl font-bold text-gray-900">{currentStats.couplingValue}</p>
              </div>
              <div className="bg-purple-100 p-3 rounded-full">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">System complexity metric</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Test Cases</p>
                <p className="text-3xl font-bold text-gray-900">{currentStats.totalTestCases.toLocaleString()}</p>
              </div>
              <div className="bg-indigo-100 p-3 rounded-full">
                <TestTube className="w-6 h-6 text-indigo-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Project Coverage</p>
                <p className="text-3xl font-bold text-gray-900">{currentStats.projectCoverage}%</p>
              </div>
              <div className="bg-green-100 p-3 rounded-full">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: `${currentStats.projectCoverage}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active MRs</p>
                <p className="text-3xl font-bold text-gray-900">{currentStats.activeMRs}</p>
              </div>
              <div className="bg-orange-100 p-3 rounded-full">
                <GitMerge className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Recent MRs */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Merge Requests</h2>
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    MR ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Author
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Coverage
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Severity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Changed Classes
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentMRs.map((mr) => (
                  <tr key={mr.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {mr.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {mr.author}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {mr.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        mr.coverage >= 90 ? 'bg-green-100 text-green-800' :
                        mr.coverage >= 80 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {mr.coverage}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        mr.severity === 'Low' ? 'bg-green-100 text-green-800' :
                        mr.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {mr.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="flex flex-wrap gap-1">
                        {mr.changedClasses.map((className, index) => (
                          <span key={index} className="inline-flex px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                            {className}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;