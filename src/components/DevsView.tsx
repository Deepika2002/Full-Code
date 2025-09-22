import React, { useState } from 'react';
import { useEffect } from 'react';
import { Search, AlertTriangle, Play, FileText, Target } from 'lucide-react';
import { apiService } from '../services/api';

const DevsView = () => {
  const [selectedMR, setSelectedMR] = useState('MR-001');
  const [selectedTestFlow, setSelectedTestFlow] = useState('');
  const [impactData, setImpactData] = useState<Record<string, any>>({});
  const [codeChanges, setCodeChanges] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch impact map data
        const impactMapData = await apiService.getImpactMap();
        
        // Transform data for component use
        const transformedImpactData: Record<string, any> = {};
        const transformedCodeChanges: Record<string, any> = {};
        
        for (const mr of impactMapData) {
          // Get detailed code changes for each MR
          try {
            const codeDetails = await apiService.getCodeChangeDetails(mr.mrId);
            
            transformedImpactData[mr.mrId] = {
              affectedClasses: mr.affectedClasses,
              severityScore: mr.severityScore,
              testFlows: codeDetails.testFlows,
              codeCoverage: mr.codeCoverage
            };
            
            transformedCodeChanges[mr.mrId] = codeDetails.codeChanges;
          } catch (err) {
            console.warn(`Failed to fetch details for MR ${mr.mrId}:`, err);
            // Use fallback data
            transformedImpactData[mr.mrId] = {
              affectedClasses: mr.affectedClasses,
              severityScore: mr.severityScore,
              testFlows: [
                { id: 'TF-001', name: 'Core Functionality Flow', status: 'pending' }
              ],
              codeCoverage: mr.codeCoverage
            };
            
            transformedCodeChanges[mr.mrId] = [
              {
                file: 'Loading...',
                changes: '+? -?',
                type: 'modified',
                preview: 'Code change details loading...'
              }
            ];
          }
        }
        
        setImpactData(transformedImpactData);
        setCodeChanges(transformedCodeChanges);
        
        // Set first MR as selected if available
        if (impactMapData.length > 0) {
          setSelectedMR(impactMapData[0].mrId);
        }
        
      } catch (err) {
        console.error('Error fetching devs view data:', err);
        setError('Failed to load impact analysis data. Please check if the backend services are running.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleTestFlowSubmit = async () => {
    if (selectedTestFlow) {
      try {
        await apiService.selectTestFlow(selectedTestFlow, selectedMR);
        alert(`Submitted test flow: ${selectedTestFlow} for execution`);
      } catch (err) {
        console.error('Error submitting test flow:', err);
        alert('Failed to submit test flow. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading impact analysis data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <h3 className="text-red-800 font-medium">Error Loading Impact Analysis</h3>
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

  const currentData = impactData[selectedMR] || impactData['MR-001'];
  const currentChanges = codeChanges[selectedMR] || codeChanges['MR-001'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Developer Impact Analysis</h2>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select 
              value={selectedMR}
              onChange={(e) => setSelectedMR(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {Object.keys(impactData).map((mrId) => (
                <option key={mrId} value={mrId}>
                  {mrId} - {impactData[mrId]?.affectedClasses?.[0]?.name || 'Unknown'} Updates
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Impact Map with Severity Score */}
      <section>
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Impact Map & Severity Analysis</h3>
            <div className="flex items-center space-x-2">
              <AlertTriangle className={`w-5 h-5 ${
                (currentData?.severityScore || 0) >= 7 ? 'text-red-500' :
                (currentData?.severityScore || 0) >= 5 ? 'text-yellow-500' :
                'text-green-500'
              }`} />
              <span className="text-lg font-bold text-gray-900">
                Severity Score: {(currentData?.severityScore || 0).toFixed(1)}/10
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Affected Classes */}
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Affected Classes</h4>
              <div className="space-y-3">
                {(currentData?.affectedClasses || []).map((cls: any, index: number) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{cls.name}</span>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        cls.severity === 'High' ? 'bg-red-100 text-red-800' :
                        cls.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {cls.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{cls.reason}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Code Coverage */}
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Code Coverage for Impact</h4>
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="text-center mb-4">
                  <div className="text-4xl font-bold text-gray-900 mb-2">
                    {(currentData?.codeCoverage || 0).toFixed(1)}%
                  </div>
                  <p className="text-sm text-gray-600">Overall Coverage</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                  <div 
                    className={`h-3 rounded-full ${
                      (currentData?.codeCoverage || 0) >= 90 ? 'bg-green-500' :
                      (currentData?.codeCoverage || 0) >= 80 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${currentData?.codeCoverage || 0}%` }}
                  ></div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-center text-sm">
                  <div>
                    <div className="font-semibold text-green-600">Lines</div>
                    <div className="text-gray-600">94.2%</div>
                  </div>
                  <div>
                    <div className="font-semibold text-yellow-600">Branches</div>
                    <div className="text-gray-600">87.8%</div>
                  </div>
                  <div>
                    <div className="font-semibold text-blue-600">Functions</div>
                    <div className="text-gray-600">95.1%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Code Change Details */}
      <section>
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Code Change Details</h3>
          <div className="space-y-4">
            {(currentChanges || []).map((change: any, index: number) => (
              <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-4 h-4 text-gray-400" />
                    <span className="font-medium text-gray-900">{change.file}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-green-600 font-medium">
                      {change.changes}
                    </span>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      change.type === 'modified' ? 'bg-blue-100 text-blue-800' :
                      change.type === 'added' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {change.type}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 ml-7">{change.preview}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Test Flows */}
      <section>
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Test Flows</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Available Test Flows</h4>
              <div className="space-y-3">
                {(currentData?.testFlows || []).map((flow: any) => (
                  <div key={flow.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        name="testFlow"
                        value={flow.id}
                        checked={selectedTestFlow === flow.id}
                        onChange={(e) => setSelectedTestFlow(e.target.value)}
                        className="text-blue-600 focus:ring-blue-500"
                      />
                      <div>
                        <div className="font-medium text-gray-900">{flow.name}</div>
                        <div className="text-sm text-gray-500">{flow.id}</div>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      flow.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      flow.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      flow.status === 'completed' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {flow.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-4">Execute Selected Test Flow</h4>
              <div className="bg-gray-50 rounded-lg p-6">
                {selectedTestFlow ? (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Target className="w-5 h-5 text-blue-600" />
                      <span className="font-medium text-gray-900">
                        Selected: {(currentData?.testFlows || []).find((f: any) => f.id === selectedTestFlow)?.name}
                      </span>
                    </div>
                    <button
                      onClick={handleTestFlowSubmit}
                      className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Play className="w-4 h-4" />
                      <span>Execute Test Flow</span>
                    </button>
                  </div>
                ) : (
                  <div className="text-center text-gray-500">
                    <Target className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <p>Select a test flow to execute</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DevsView;