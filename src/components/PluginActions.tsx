import React, { useState } from 'react';
import { GitBranch, Send, Database, RefreshCw, CheckCircle, AlertCircle, Clock, Instagram as Diagram } from 'lucide-react';

const PluginActions = () => {
  const [isSendingGraph, setIsSendingGraph] = useState(false);
  const [isSendingDiff, setIsSendingDiff] = useState(false);
  const [graphStatus, setGraphStatus] = useState('idle'); // idle, generating, success, error
  const [diffStatus, setDiffStatus] = useState('idle');
  const [gitDiffData, setGitDiffData] = useState('');

  const handleSendGraph = async () => {
    setIsSendingGraph(true);
    setGraphStatus('sending');
    
    // Simulate API call to Microservice-1
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      setGraphStatus('success');
      setTimeout(() => setGraphStatus('idle'), 3000);
    } catch (error) {
      setGraphStatus('error');
      setTimeout(() => setGraphStatus('idle'), 3000);
    } finally {
      setIsSendingGraph(false);
    }
  };

  const handleSendDiff = async () => {
    if (!gitDiffData.trim()) {
      alert('Please enter git diff data');
      return;
    }

    setIsSendingDiff(true);
    setDiffStatus('generating');
    
    // Simulate API call to Microservice-2
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      setDiffStatus('success');
      setTimeout(() => setDiffStatus('idle'), 3000);
    } catch (error) {
      setDiffStatus('error');
      setTimeout(() => setDiffStatus('idle'), 3000);
    } finally {
      setIsSendingDiff(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'sending':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusMessage = (status, type) => {
    switch (status) {
      case 'sending':
        return type === 'graph' ? 'Sending dependency graph to Microservice-1...' : 'Processing git diff...';
      case 'success':
        return type === 'graph' ? 'Dependency graph sent successfully!' : 'Git diff processed successfully!';
      case 'error':
        return type === 'graph' ? 'Failed to send dependency graph' : 'Failed to process git diff';
      default:
        return '';
    }
  };

  const sampleGitDiff = `diff --git a/src/main/java/com/ecommerce/service/UserService.java b/src/main/java/com/ecommerce/service/UserService.java
index 1234567..abcdefg 100644
--- a/src/main/java/com/ecommerce/service/UserService.java
+++ b/src/main/java/com/ecommerce/service/UserService.java
@@ -45,6 +45,12 @@ public class UserService {
     }
 
     public User createUser(UserDto userDto) {
+        // Add email validation
+        if (!isValidEmail(userDto.getEmail())) {
+            throw new InvalidEmailException("Invalid email format");
+        }
+        
+        // Encrypt password before saving
         User user = new User();
         user.setEmail(userDto.getEmail());
-        user.setPassword(userDto.getPassword());
+        user.setPassword(encryptPassword(userDto.getPassword()));
         return userRepository.save(user);
     }`;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">GitVortex Plugin Actions</h2>
        <p className="text-gray-600">Automate dependency graph creation and send git diff data to microservices</p>
      </div>

      {/* Plugin Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Action 1: Send Dependency Graph */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-blue-100 p-3 rounded-full">
              <Diagram className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Send Dependency Graph</h3>
              <p className="text-sm text-gray-600">Extract from IntelliJ & Push to Microservice-Index</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Process Overview:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Extract dependency graph from IntelliJ</li>
                <li>• Parse graph data and create dependency index</li>
                <li>• Generate text embeddings using AI model</li>
                <li>• Store vectors in RAG database</li>
                <li>• Schedule daily refresh</li>
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-start space-x-2">
                <Diagram className="w-4 h-4 text-blue-600 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <strong>IntelliJ Integration:</strong> Right-click project folder → Diagrams → Show Diagrams. 
                  The plugin will automatically extract this dependency graph data.
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getStatusIcon(graphStatus)}
                <span className="text-sm text-gray-600">
                  {getStatusMessage(graphStatus, 'graph') || 'Ready to extract and send dependency graph'}
                </span>
              </div>
            </div>

            <button
              onClick={handleSendGraph}
              disabled={isSendingGraph}
              className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                isSendingGraph
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isSendingGraph ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Extract & Send Dependency Graph</span>
                </>
              )}
            </button>

            {graphStatus === 'success' && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-green-800">
                    Dependency graph successfully extracted from IntelliJ and sent to Microservice-Index
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action 2: Send Git Diff */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-green-100 p-3 rounded-full">
              <GitBranch className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Git Diff Processing</h3>
              <p className="text-sm text-gray-600">Send to Microservice-MR (Service 2)</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Process Overview:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Extract code changes from git diff</li>
                <li>• Generate MR analysis prompt</li>
                <li>• Call AI service for impact analysis</li>
                <li>• Store results in MR table</li>
                <li>• Update changed class names</li>
              </ul>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Git Diff Data:
              </label>
              <div className="relative">
                <textarea
                  value={gitDiffData}
                  onChange={(e) => setGitDiffData(e.target.value)}
                  placeholder="Paste your git diff here..."
                  className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent font-mono text-sm"
                />
                <button
                  onClick={() => setGitDiffData(sampleGitDiff)}
                  className="absolute top-2 right-2 text-xs text-blue-600 hover:text-blue-800"
                >
                  Use Sample
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getStatusIcon(diffStatus)}
                <span className="text-sm text-gray-600">
                  {getStatusMessage(diffStatus, 'diff') || 'Ready to process git diff'}
                </span>
              </div>
            </div>

            <button
              onClick={handleSendDiff}
              disabled={isSendingDiff || !gitDiffData.trim()}
              className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                isSendingDiff || !gitDiffData.trim()
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isSendingDiff ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Send Git Diff Data</span>
                </>
              )}
            </button>

            {diffStatus === 'success' && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-green-800">
                    Git diff successfully processed by Microservice-MR
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Microservices Status */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Microservices Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            { name: 'Microservice-Index', status: 'online', description: 'Dependency graph & embeddings' },
            { name: 'Microservice-MR', status: 'online', description: 'MR triggered analysis' },
            { name: 'Microservice-Common', status: 'online', description: 'Frontend API gateway' },
            { name: 'Microservice-AI', status: 'online', description: 'Impact analysis & coverage' },
            { name: 'Microservice-TestCase', status: 'online', description: 'Test execution & monitoring' }
          ].map((service, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <div className={`w-2 h-2 rounded-full ${
                  service.status === 'online' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span className="font-medium text-gray-900 text-sm">{service.name}</span>
              </div>
              <p className="text-xs text-gray-600">{service.description}</p>
              <div className="mt-2">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  service.status === 'online' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {service.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Database Schema Info */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Database Schema Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              name: 'TestFlowsTable',
              fields: ['TestFlowName', 'FileName'],
              description: 'Test flow definitions'
            },
            {
              name: 'MRTable',
              fields: ['author', 'timestamp', 'totalUnitTestCoverage', 'mrID', 'changedClassNames', 'severityScore'],
              description: 'Merge request data'
            },
            {
              name: 'DailyMetricsTable',
              fields: ['dayId', 'couplingValue', 'totNoOfTestCases', 'MRCountDayWise'],
              description: 'Daily statistics'
            },
            {
              name: 'VectorDB',
              fields: ['embeddings', 'metadata', 'similarity_search'],
              description: 'RAG vector storage'
            }
          ].map((table, index) => (
            <div key={index} className="border rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">{table.name}</h4>
              <p className="text-xs text-gray-600 mb-3">{table.description}</p>
              <div className="space-y-1">
                {table.fields.map((field, fieldIndex) => (
                  <div key={fieldIndex} className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                    {field}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PluginActions;