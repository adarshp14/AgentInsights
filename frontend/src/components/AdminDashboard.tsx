import { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  Trash2, 
  Database, 
  BarChart3, 
  Settings,
  AlertCircle,
  RefreshCw,
  LogOut
} from 'lucide-react';

interface Document {
  document_id: string;
  filename: string;
  file_type: string;
  upload_time: string;
  file_size: number;
  total_chunks: number;
  chunk_count: number;
}

interface VectorStats {
  collection_name: string;
  total_chunks: number;
  total_documents: number;
  total_size_bytes: number;
  file_types: Record<string, number>;
  embedding_model: string;
  vector_dimension: number;
  database_type: string;
}

interface AdminDashboardProps {
  authToken: string;
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ authToken, onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [vectorStats, setVectorStats] = useState<VectorStats | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [showConfirmReset, setShowConfirmReset] = useState(false);

  const apiHeaders = {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch('/api/documents/list');
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const fetchVectorStats = async () => {
    try {
      const response = await fetch('/api/documents/stats');
      const data = await response.json();
      setVectorStats(data);
    } catch (error) {
      console.error('Error fetching vector stats:', error);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/admin/dashboard/stats', {
        headers: apiHeaders
      });
      const data = await response.json();
      setVectorStats(data.vector_store);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  useEffect(() => {
    fetchDocuments();
    fetchVectorStats();
    fetchDashboardData();
  }, []);

  const handleFileUpload = async () => {
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadStatus('');

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);

      const response = await fetch('/api/admin/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        },
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        setUploadStatus(`✅ Successfully uploaded ${data.filename} (${data.chunks_created} chunks created)`);
        setUploadFile(null);
        fetchDocuments();
        fetchVectorStats();
      } else {
        setUploadStatus(`❌ Upload failed: ${data.error}`);
      }
    } catch (error) {
      setUploadStatus(`❌ Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      const response = await fetch(`/api/admin/documents/${documentId}`, {
        method: 'DELETE',
        headers: apiHeaders
      });

      if (response.ok) {
        setUploadStatus(`✅ Document deleted successfully`);
        fetchDocuments();
        fetchVectorStats();
      } else {
        setUploadStatus(`❌ Failed to delete document`);
      }
    } catch (error) {
      setUploadStatus(`❌ Delete error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleResetVectorStore = async () => {
    try {
      const response = await fetch('/api/admin/documents/reset', {
        method: 'POST',
        headers: apiHeaders
      });

      if (response.ok) {
        setUploadStatus(`✅ Vector store reset successfully`);
        setShowConfirmReset(false);
        fetchDocuments();
        fetchVectorStats();
      } else {
        setUploadStatus(`❌ Failed to reset vector store`);
      }
    } catch (error) {
      setUploadStatus(`❌ Reset error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'documents', name: 'Documents', icon: FileText },
    { id: 'upload', name: 'Upload', icon: Upload },
    { id: 'settings', name: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">InsightFlow Knowledge Base Management</p>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-red-600 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status message */}
        {uploadStatus && (
          <div className="mb-6 p-4 rounded-lg bg-gray-100 text-gray-800">
            {uploadStatus}
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <Database className="w-8 h-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Documents</p>
                    <p className="text-2xl font-bold text-gray-900">{vectorStats?.total_documents || 0}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <FileText className="w-8 h-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Chunks</p>
                    <p className="text-2xl font-bold text-gray-900">{vectorStats?.total_chunks || 0}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Storage Used</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatFileSize(vectorStats?.total_size_bytes || 0)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <Settings className="w-8 h-8 text-orange-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Vector Dimension</p>
                    <p className="text-2xl font-bold text-gray-900">{vectorStats?.vector_dimension || 0}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600">Database Type</p>
                  <p className="text-gray-900">{vectorStats?.database_type || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Embedding Model</p>
                  <p className="text-gray-900">{vectorStats?.embedding_model || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Collection Name</p>
                  <p className="text-gray-900">{vectorStats?.collection_name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">File Types</p>
                  <p className="text-gray-900">
                    {vectorStats?.file_types ? Object.entries(vectorStats.file_types).map(([type, count]) => 
                      `${type}: ${count}`
                    ).join(', ') : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Document Management</h2>
              <button
                onClick={() => {
                  fetchDocuments();
                  fetchVectorStats();
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Document
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Chunks
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Upload Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {documents.map((doc) => (
                    <tr key={doc.document_id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <FileText className="w-5 h-5 text-gray-400 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                            <div className="text-sm text-gray-500">{doc.document_id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                          {doc.file_type.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatFileSize(doc.file_size)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {doc.chunk_count} / {doc.total_chunks}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(doc.upload_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => handleDeleteDocument(doc.document_id)}
                          className="text-red-600 hover:text-red-900 flex items-center space-x-1"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Delete</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {documents.length === 0 && (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
                  <p className="text-gray-500">Upload your first document to get started.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Document
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.txt,.docx"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Supported formats: PDF, TXT, DOCX (Max 10MB)
                  </p>
                </div>

                {uploadFile && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{uploadFile.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(uploadFile.size)}</p>
                      </div>
                      <button
                        onClick={handleFileUpload}
                        disabled={isUploading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                      >
                        {isUploading ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            <span>Uploading...</span>
                          </>
                        ) : (
                          <>
                            <Upload className="w-4 h-4" />
                            <span>Upload</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex">
                <AlertCircle className="w-5 h-5 text-yellow-400 mr-3" />
                <div>
                  <h3 className="text-sm font-medium text-yellow-800">Upload Guidelines</h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <ul className="list-disc list-inside space-y-1">
                      <li>Documents will be automatically chunked and embedded</li>
                      <li>Existing documents with the same content will be updated</li>
                      <li>Processing time depends on document size and complexity</li>
                      <li>All documents are searchable immediately after upload</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Settings</h2>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Vector Store Management</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
                  <div>
                    <h4 className="text-sm font-medium text-red-800">Reset Vector Store</h4>
                    <p className="text-sm text-red-600">
                      This will permanently delete all documents and embeddings. This action cannot be undone.
                    </p>
                  </div>
                  <button
                    onClick={() => setShowConfirmReset(true)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    Reset Store
                  </button>
                </div>
              </div>

              {/* Confirmation Modal */}
              {showConfirmReset && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                  <div className="bg-white rounded-lg p-6 max-w-md w-full">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Confirm Reset</h3>
                    <p className="text-gray-600 mb-6">
                      Are you absolutely sure you want to reset the vector store? This will permanently delete:
                    </p>
                    <ul className="list-disc list-inside text-sm text-gray-600 mb-6 space-y-1">
                      <li>All uploaded documents</li>
                      <li>All generated embeddings</li>
                      <li>All vector search indices</li>
                    </ul>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => setShowConfirmReset(false)}
                        className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleResetVectorStore}
                        className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                      >
                        Reset Store
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};