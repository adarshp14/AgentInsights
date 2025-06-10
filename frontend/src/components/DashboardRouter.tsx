import React, { useState, useEffect } from 'react';
import { AdminDashboardLayout } from './AdminDashboardLayout';
import { EmployeeDashboardLayout } from './EmployeeDashboardLayout';
import { UserManagement } from './UserManagement';
import { StreamingChatInterface } from './StreamingChatInterface';
import { DocumentUpload } from './DocumentUpload';
import { RealtimeDashboard } from './RealtimeDashboard';
import {
  BarChart3,
  Users,
  FileText,
  Settings,
  MessageSquare,
  TrendingUp,
  Clock,
  CheckCircle,
  Upload,
  Search,
  Bookmark,
  User,
  Activity,
  AlertCircle,
  Trash2
} from 'lucide-react';

interface DashboardRouterProps {
  currentUser: {
    user_id: string;
    email: string;
    full_name: string;
    role: string;
    org_id: string;
    org_name: string;
  };
  onLogout: () => void;
}

export const DashboardRouter: React.FC<DashboardRouterProps> = ({ currentUser, onLogout }) => {
  const [activeTab, setActiveTab] = useState(currentUser.role === 'admin' ? 'overview' : 'chat');

  // Admin Dashboard Content
  const renderAdminContent = () => {
    switch (activeTab) {
      case 'overview':
        return <AdminOverview currentUser={currentUser} />;
      case 'users':
        return <UserManagement currentUser={currentUser} />;
      case 'documents':
        return <DocumentManagement currentUser={currentUser} />;
      case 'analytics':
        return <RealtimeDashboard />;
      case 'settings':
        return <OrganizationSettings currentUser={currentUser} />;
      default:
        return <AdminOverview currentUser={currentUser} />;
    }
  };

  // Employee Dashboard Content
  const renderEmployeeContent = () => {
    switch (activeTab) {
      case 'chat':
        return <StreamingChatInterface conversationId={`user_${currentUser.user_id}`} />;
      case 'documents':
        return <DocumentBrowser currentUser={currentUser} />;
      case 'history':
        return <QueryHistory currentUser={currentUser} />;
      case 'bookmarks':
        return <Bookmarks currentUser={currentUser} />;
      case 'profile':
        return <UserProfile currentUser={currentUser} />;
      default:
        return <StreamingChatInterface conversationId={`user_${currentUser.user_id}`} />;
    }
  };

  if (currentUser.role === 'admin') {
    return (
      <AdminDashboardLayout
        currentUser={currentUser}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onLogout={onLogout}
      >
        {renderAdminContent()}
      </AdminDashboardLayout>
    );
  }

  return (
    <EmployeeDashboardLayout
      currentUser={currentUser}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      onLogout={onLogout}
    >
      {renderEmployeeContent()}
    </EmployeeDashboardLayout>
  );
};

// Admin Overview Dashboard
const AdminOverview: React.FC<{ currentUser: any }> = ({ currentUser }) => {
  const metrics = [
    {
      title: 'Total Users',
      value: '24',
      change: '+2 this week',
      icon: Users,
      color: 'bg-blue-500'
    },
    {
      title: 'Documents',
      value: '156',
      change: '+12 this month',
      icon: FileText,
      color: 'bg-green-500'
    },
    {
      title: 'Queries Today',
      value: '342',
      change: '+18% from yesterday',
      icon: MessageSquare,
      color: 'bg-purple-500'
    },
    {
      title: 'Response Time',
      value: '1.2s',
      change: '-0.3s improvement',
      icon: Clock,
      color: 'bg-orange-500'
    }
  ];

  const recentActivity = [
    { action: 'New user registered', user: 'Alice Johnson', time: '2 minutes ago' },
    { action: 'Document uploaded', user: 'Bob Smith', time: '15 minutes ago' },
    { action: 'User promoted to admin', user: 'Carol Davis', time: '1 hour ago' },
    { action: 'System backup completed', user: 'System', time: '2 hours ago' }
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl text-white p-6">
        <h2 className="text-2xl font-bold mb-2">Welcome back, {currentUser.full_name}!</h2>
        <p className="text-indigo-100">Here's what's happening with {currentUser.org_name} today.</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                  <p className="text-3xl font-bold text-gray-900">{metric.value}</p>
                  <p className="text-sm text-green-600 mt-1">{metric.change}</p>
                </div>
                <div className={`p-3 rounded-lg ${metric.color}`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full flex items-center space-x-3 p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-left">
              <div className="p-2 bg-blue-500 rounded-lg">
                <Users className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="font-medium text-gray-900">Invite Team Member</p>
                <p className="text-sm text-gray-500">Add new users to your organization</p>
              </div>
            </button>
            
            <button className="w-full flex items-center space-x-3 p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors text-left">
              <div className="p-2 bg-green-500 rounded-lg">
                <Upload className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="font-medium text-gray-900">Upload Documents</p>
                <p className="text-sm text-gray-500">Add knowledge base content</p>
              </div>
            </button>
            
            <button className="w-full flex items-center space-x-3 p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors text-left">
              <div className="p-2 bg-purple-500 rounded-lg">
                <BarChart3 className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="font-medium text-gray-900">View Analytics</p>
                <p className="text-sm text-gray-500">Check usage statistics</p>
              </div>
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-sm text-gray-500">{activity.user} • {activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Document Management Component
const DocumentManagement: React.FC<{ currentUser: any }> = ({ currentUser }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadStats, setUploadStats] = useState({
    totalDocuments: 0,
    totalSizeMB: 0,
    processingCount: 0,
    successCount: 0,
    errorCount: 0
  });
  const [showUploadModal, setShowUploadModal] = useState(false);

  // Mock data - replace with API call to get organization documents
  useEffect(() => {
    const mockDocuments = [
      {
        doc_id: '1',
        filename: 'Company_Handbook.pdf',
        file_size: 2.5,
        upload_date: '2024-01-15T10:30:00Z',
        status: 'processed',
        chunks_count: 45,
        uploaded_by: 'John Admin'
      },
      {
        doc_id: '2', 
        filename: 'Product_Specifications.docx',
        file_size: 1.8,
        upload_date: '2024-01-14T15:20:00Z',
        status: 'processing',
        chunks_count: 0,
        uploaded_by: 'Jane Doe'
      },
      {
        doc_id: '3',
        filename: 'Meeting_Notes.txt',
        file_size: 0.3,
        upload_date: '2024-01-13T09:15:00Z',
        status: 'error',
        error_message: 'File format not supported',
        chunks_count: 0,
        uploaded_by: 'Bob Smith'
      }
    ];

    setTimeout(() => {
      setDocuments(mockDocuments);
      setUploadStats({
        totalDocuments: mockDocuments.length,
        totalSizeMB: mockDocuments.reduce((sum, doc) => sum + doc.file_size, 0),
        processingCount: mockDocuments.filter(d => d.status === 'processing').length,
        successCount: mockDocuments.filter(d => d.status === 'processed').length,
        errorCount: mockDocuments.filter(d => d.status === 'error').length
      });
      setLoading(false);
    }, 1000);
  }, [currentUser.org_id]);

  const handleUploadComplete = (newDoc) => {
    setDocuments(prev => [newDoc, ...prev]);
    setUploadStats(prev => ({
      ...prev,
      totalDocuments: prev.totalDocuments + 1,
      totalSizeMB: prev.totalSizeMB + (newDoc.file_size || 0),
      processingCount: prev.processingCount + 1
    }));
  };

  const handleDeleteDocument = async (docId) => {
    if (confirm('Are you sure you want to delete this document?')) {
      // TODO: Call delete API
      setDocuments(prev => prev.filter(doc => doc.doc_id !== docId));
    }
  };

  const getStatusBadge = (status, errorMessage) => {
    switch (status) {
      case 'processed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Processed
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3 mr-1 animate-spin" />
            Processing
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <AlertCircle className="w-3 h-3 mr-1" />
            Error
          </span>
        );
      default:
        return null;
    }
  };

  const formatFileSize = (sizeMB) => {
    if (sizeMB < 1) return `${(sizeMB * 1024).toFixed(0)} KB`;
    return `${sizeMB.toFixed(1)} MB`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900">{uploadStats.totalDocuments}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Processed</p>
              <p className="text-2xl font-bold text-gray-900">{uploadStats.successCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Processing</p>
              <p className="text-2xl font-bold text-gray-900">{uploadStats.processingCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900">{formatFileSize(uploadStats.totalSizeMB)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Header Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Document Library</h3>
            <p className="text-sm text-gray-600">Manage your organization's knowledge base documents</p>
          </div>
          
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload Documents
          </button>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chunks
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.doc_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-gray-600" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                        <div className="text-sm text-gray-500">Uploaded by {doc.uploaded_by}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(doc.status, doc.error_message)}
                    {doc.status === 'error' && doc.error_message && (
                      <div className="text-xs text-red-600 mt-1">{doc.error_message}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatFileSize(doc.file_size)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(doc.upload_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {doc.chunks_count > 0 ? `${doc.chunks_count} chunks` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => handleDeleteDocument(doc.doc_id)}
                      className="text-red-600 hover:text-red-900 p-1 rounded-lg hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {documents.length === 0 && (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No documents uploaded</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by uploading your first document to the knowledge base.
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload Document
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowUploadModal(false)} />
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                      Upload Documents
                    </h3>
                    <DocumentUpload 
                      onUploadComplete={(doc) => {
                        handleUploadComplete(doc);
                        setShowUploadModal(false);
                      }} 
                    />
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Organization Settings Component
const OrganizationSettings: React.FC<{ currentUser: any }> = ({ currentUser }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Organization Settings</h3>
        
        <div className="space-y-6">
          {/* Organization Info */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Organization Information</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Organization Name</label>
                <input
                  type="text"
                  defaultValue={currentUser.org_name}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Domain</label>
                <input
                  type="text"
                  defaultValue="company.com"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* AI Settings */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">AI Configuration</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Response Style</label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                  <option value="balanced">Balanced</option>
                  <option value="concise">Concise</option>
                  <option value="detailed">Detailed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Similarity Threshold</label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  defaultValue="0.7"
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Less Strict</span>
                  <span>More Strict</span>
                </div>
              </div>
            </div>
          </div>

          <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

// Employee Components (Simplified)
const DocumentBrowser: React.FC<{ currentUser: any }> = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Knowledge Base</h3>
    <p className="text-gray-600">Browse and search organizational documents...</p>
  </div>
);

const QueryHistory: React.FC<{ currentUser: any }> = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Query History</h3>
    <p className="text-gray-600">View your previous questions and responses...</p>
  </div>
);

const Bookmarks: React.FC<{ currentUser: any }> = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Bookmarks</h3>
    <p className="text-gray-600">Your saved responses and useful information...</p>
  </div>
);

const UserProfile: React.FC<{ currentUser: any }> = ({ currentUser }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Settings</h3>
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
        <input
          type="text"
          defaultValue={currentUser.full_name}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
        <input
          type="email"
          defaultValue={currentUser.email}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
        Update Profile
      </button>
    </div>
  </div>
);