import React from 'react';
import { useState, useEffect } from 'react';
import { TrendingUp, GitMerge, TestTube, Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import { apiService } from '../services/api';

const Dashboard = () => {
  const [yesterdayStats, setYesterdayStats] = useState({
    totalMRs: 0,
    unitTestCoverage: 0,
    passedTests: 0,
    failedTests: 0
  });

  const [currentStats, setCurrentStats] = useState({
    couplingValue: 0,
    totalTestCases: 0,
    projectCoverage: 0,
    activeMRs: 0
  });

  const [recentMRs, setRecentMRs] = useState<Array<{
    mrId: string;
    author: string;
    timestamp: string;
    codeCoverage: number;
    severityScore: number;
    affectedClasses: Array<{ name: string; severity: string; reason: string }>;
  }>>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch yesterday's stats
        const yesterdayData = await apiService.getYesterdayStats();
        setYesterdayStats(yesterdayData);

        // Fetch current stats
        const currentData = await apiService.getCurrentStats();
        setCurrentStats(currentData);

        // Fetch recent MRs from impact map
        const impactData = await apiService.getImpactMap();
        setRecentMRs(impactData.slice(0, 3)); // Show only first 3

      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please check if the backend services are running.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <h3 className="text-red-800 font-medium">Error Loading Dashboard</h3>
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
                    {mr.mrId}
              <div className="bg-orange-100 p-3 rounded-full">
                <GitMerge className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
                    {new Date(mr.timestamp).toLocaleString()}
          </div>
      </section>

      {/* Recent MRs */}
                      mr.codeCoverage >= 90 ? 'bg-green-100 text-green-800' :
                      mr.codeCoverage >= 80 ? 'bg-yellow-100 text-yellow-800' :
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
                      {mr.codeCoverage.toFixed(1)}%
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    MR ID
                      mr.severityScore <= 3 ? 'bg-green-100 text-green-800' :
                      mr.severityScore <= 7 ? 'bg-yellow-100 text-yellow-800' :
                    Author
                  </th>
                      {mr.severityScore <= 3 ? 'Low' : mr.severityScore <= 7 ? 'Medium' : 'High'}
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Coverage
                      {mr.affectedClasses.slice(0, 3).map((affectedClass, index) => (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {affectedClass.name}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {mr.affectedClasses.length > 3 && (
                        <span className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                          +{mr.affectedClasses.length - 3} more
                        </span>
                      )}
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