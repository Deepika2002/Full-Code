import React, { useState } from 'react';
import { Search, AlertTriangle, Play, FileText, Target } from 'lucide-react';

const DevsView = () => {
  const [selectedMR, setSelectedMR] = useState('MR-001');
  const [selectedTestFlow, setSelectedTestFlow] = useState('');

  const impactData = {
    'MR-001': {
      affectedClasses: [
        { name: 'UserService', severity: 'High', reason: 'Core business logic changes' },
        { name: 'PaymentController', severity: 'Medium', reason: 'API endpoint modifications' },
        { name: 'OrderEntity', severity: 'Low', reason: 'Data model updates' }
      ],
      severityScore: 7.8,
      testFlows: [
        { id: 'TF-001', name: 'User Registration Flow', status: 'pending' },
        { id: 'TF-002', name: 'Payment Processing Flow', status: 'pending' },
        { id: 'TF-003', name: 'Order Management Flow', status: 'pending' }
      ],
      codeCoverage: 92.1
    },
    'MR-002': {
      affectedClasses: [
        { name: 'ProductRepository', severity: 'Medium', reason: 'Database query changes' },
        { name: 'CategoryService', severity: 'Low', reason: 'Minor logic updates' }
      ],
      severityScore: 4.2,
      testFlows: [
        { id: 'TF-004', name: 'Product Catalog Flow', status: 'pending' },
        { id: 'TF-005', name: 'Category Management Flow', status: 'pending' }
      ],
      codeCoverage: 85.7
    }
  };

  const codeChanges = {
    'MR-001': [
      {
        file: 'src/main/java/com/ecommerce/service/UserService.java',
        changes: '+15 -8',
        type: 'modified',
        preview: 'Added email validation and password encryption logic'
      },
      {
        file: 'src/main/java/com/ecommerce/controller/PaymentController.java',
        changes: '+23 -12',
        type: 'modified',
        preview: 'Updated payment processing endpoints with new validation'
      },
      {
        file: 'src/main/java/com/ecommerce/entity/OrderEntity.java',
        changes: '+5 -2',
        type: 'modified',
        preview: 'Added new fields for order tracking'
      }
    ]
  };

  const handleTestFlowSubmit = () => {
    if (selectedTestFlow) {
      alert(`Submitted test flow: ${selectedTestFlow} for execution`);
    }
  };

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
              <option value="MR-001">MR-001 - UserService Updates</option>
              <option value="MR-002">MR-002 - Product Repository</option>
              <option value="MR-003">MR-003 - Security Config</option>
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
                currentData.severityScore >= 7 ? 'text-red-500' :
                currentData.severityScore >= 5 ? 'text-yellow-500' :
                'text-green-500'
              }`} />
              <span className="text-lg font-bold text-gray-900">
                Severity Score: {currentData.severityScore}/10
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Affected Classes */}
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Affected Classes</h4>
              <div className="space-y-3">
                {currentData.affectedClasses.map((cls, index) => (
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
                    {currentData.codeCoverage}%
                  </div>
                  <p className="text-sm text-gray-600">Overall Coverage</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                  <div 
                    className={`h-3 rounded-full ${
                      currentData.codeCoverage >= 90 ? 'bg-green-500' :
                      currentData.codeCoverage >= 80 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${currentData.codeCoverage}%` }}
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
            {currentChanges.map((change, index) => (
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
                {currentData.testFlows.map((flow) => (
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
                        Selected: {currentData.testFlows.find(f => f.id === selectedTestFlow)?.name}
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