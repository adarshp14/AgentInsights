import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  FileText,
  Clock,
  Users,
  CheckCircle,
  AlertTriangle,
  PieChart,
  Database,
  Activity
} from 'lucide-react';

interface AnalyticsDashboardProps {
  currentUser: {
    org_id: string;
    role: string;
  };
}

interface AnalyticsData {
  organization: {
    org_id: string;
    total_users: number;
    admin_users: number;
    employee_users: number;
  };
  documents: {
    total: number;
    processed: number;
    processing: number;
    failed: number;
    success_rate: number;
  };
  storage: {
    total_size_bytes: number;
    total_size_mb: number;
    total_chunks: number;
    avg_chunks_per_doc: number;
  };
  activity: {
    documents_uploaded_30d: number;
    users_added_30d: number;
    last_updated: string;
  };
}

interface DocumentType {
  file_type: string;
  document_count: number;
  total_size_mb: number;
  average_size_mb: number;
  percentage: number;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ currentUser }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [processingHealth, setProcessingHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalyticsData();
  }, [currentUser.org_id]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      // Fetch overview analytics
      const overviewResponse = await fetch('http://localhost:8001/analytics/overview', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (overviewResponse.ok) {
        const overviewData = await overviewResponse.json();
        setAnalytics(overviewData);
      }

      // Fetch document types breakdown
      const typesResponse = await fetch('http://localhost:8001/analytics/documents/types', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (typesResponse.ok) {
        const typesData = await typesResponse.json();
        setDocumentTypes(typesData.breakdown || []);
      }

      // Fetch processing health
      const healthResponse = await fetch('http://localhost:8001/analytics/processing/health', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setProcessingHealth(healthData);
      }

    } catch (error) {
      console.error('Error fetching analytics:', error);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">{error}</span>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return <div>No analytics data available</div>;
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${Math.round(bytes / (1024 * 1024))} MB`;
  };

  const getHealthColor = (rate: number) => {
    if (rate >= 90) return 'text-green-600 bg-green-100';
    if (rate >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.organization.total_users}</p>
              <p className="text-xs text-gray-500">{analytics.organization.admin_users} admins</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Documents</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.documents.total}</p>
              <p className="text-xs text-gray-500">{analytics.documents.processed} processed</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Database className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.storage.total_size_mb} MB</p>
              <p className="text-xs text-gray-500">{analytics.storage.total_chunks} chunks</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${getHealthColor(analytics.documents.success_rate)}`}>
              <CheckCircle className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.documents.success_rate}%</p>
              <p className="text-xs text-gray-500">Processing health</p>
            </div>
          </div>
        </div>
      </div>

      {/* Document Types Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <PieChart className="w-5 h-5 mr-2" />
            Document Types
          </h3>
          {documentTypes.length > 0 ? (
            <div className="space-y-3">
              {documentTypes.map((type, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      index === 0 ? 'bg-blue-500' : 
                      index === 1 ? 'bg-green-500' : 
                      index === 2 ? 'bg-purple-500' : 'bg-gray-400'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-900">
                      {type.file_type.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-gray-900">{type.document_count}</div>
                    <div className="text-xs text-gray-500">{type.percentage}%</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No documents uploaded yet</p>
          )}
        </div>

        {/* Processing Health */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Processing Health
          </h3>
          {processingHealth ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Success Rate</span>
                <span className={`text-sm font-bold px-2 py-1 rounded ${getHealthColor(processingHealth.health_metrics.success_rate)}`}>
                  {processingHealth.health_metrics.success_rate}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Currently Processing</span>
                <span className="text-sm font-bold text-gray-900">
                  {processingHealth.health_metrics.currently_processing}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Avg Processing Time</span>
                <span className="text-sm font-bold text-gray-900">
                  {processingHealth.health_metrics.average_processing_time}
                </span>
              </div>
              {processingHealth.recommendations.length > 0 && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Recommendation:</strong> {processingHealth.recommendations[0]}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">Processing data unavailable</p>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Recent Activity (Last 30 Days)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{analytics.activity.documents_uploaded_30d}</div>
            <div className="text-sm text-gray-600">Documents Uploaded</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{analytics.activity.users_added_30d}</div>
            <div className="text-sm text-gray-600">Users Added</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{analytics.storage.avg_chunks_per_doc}</div>
            <div className="text-sm text-gray-600">Avg Chunks per Doc</div>
          </div>
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-center text-xs text-gray-500">
        Last updated: {new Date(analytics.activity.last_updated).toLocaleString()}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;