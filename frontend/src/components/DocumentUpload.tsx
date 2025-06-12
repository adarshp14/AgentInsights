import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, X, File as FileIcon } from 'lucide-react';

interface UploadedDocument {
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  chunks_created: number;
  status: 'success' | 'error';
  error?: string;
}

interface DocumentUploadProps {
  onUploadComplete?: (document: UploadedDocument) => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState<string[]>([]);
  const [uploadResults, setUploadResults] = useState<UploadedDocument[]>([]);
  const [showResults, setShowResults] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    handleFileSelection(files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFileSelection(files);
    }
  };

  const handleFileSelection = (files: File[]) => {
    const validFiles = files.filter(file => {
      const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const allowedExtensions = ['.pdf', '.txt', '.docx'];
      
      return allowedTypes.includes(file.type) || 
             allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    });

    setSelectedFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (file: File): Promise<UploadedDocument> => {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await fetch('http://localhost:8001/documents/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.detail || 'Upload failed');
    }
    
    return {
      document_id: result.document_id || '',
      filename: result.filename || file.name,
      file_type: result.file_type || file.name.split('.').pop() || '',
      file_size: result.file_size || file.size,
      chunks_created: result.chunks_created || 0,
      status: result.status === 'success' ? 'success' : 'error',
      error: result.message || result.error
    };
  };

  const handleUploadAll = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(selectedFiles.map(f => f.name));
    setUploadResults([]);
    setShowResults(true);

    const results: UploadedDocument[] = [];

    for (const file of selectedFiles) {
      try {
        const result = await uploadFile(file);
        results.push(result);
        setUploadResults([...results]);
        
        if (result.status === 'success' && onUploadComplete) {
          onUploadComplete(result);
        }
      } catch (error) {
        results.push({
          document_id: '',
          filename: file.name,
          file_type: file.name.split('.').pop() || '',
          file_size: file.size,
          chunks_created: 0,
          status: 'error',
          error: error instanceof Error ? error.message : 'Upload failed'
        });
        setUploadResults([...results]);
      }
      
      setUploading(prev => prev.filter(name => name !== file.name));
    }

    setSelectedFiles([]);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FileIcon className="w-5 h-5 text-red-500" />;
      case 'docx':
        return <FileIcon className="w-5 h-5 text-blue-500" />;
      case 'txt':
        return <FileText className="w-5 h-5 text-gray-500" />;
      default:
        return <FileIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Upload Documents
        </h3>
        <p className="text-gray-600 mb-4">
          Drag and drop your files here, or click to browse
        </p>
        
        <input
          type="file"
          multiple
          accept=".pdf,.txt,.docx"
          onChange={handleFileInput}
          className="hidden"
          id="file-upload"
        />
        
        <label
          htmlFor="file-upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
        >
          Choose Files
        </label>
        
        <p className="text-xs text-gray-500 mt-2">
          Supported formats: PDF, TXT, DOCX (Max 10MB each)
        </p>
      </div>

      {selectedFiles.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium text-gray-900">
              Selected Files ({selectedFiles.length})
            </h4>
            <button
              onClick={handleUploadAll}
              disabled={uploading.length > 0}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading.length > 0 ? 'Uploading...' : 'Upload All'}
            </button>
          </div>
          
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  {getFileIcon(file.name)}
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {uploading.includes(file.name) ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-sm text-blue-600">Uploading...</span>
                    </div>
                  ) : (
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showResults && uploadResults.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium text-gray-900">Upload Results</h4>
            <button
              onClick={() => {
                setShowResults(false);
                setUploadResults([]);
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="space-y-3">
            {uploadResults.map((result, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border ${
                  result.status === 'success'
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-start space-x-3">
                  {result.status === 'success' ? (
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                  )}
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">
                        {result.filename}
                      </p>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        result.status === 'success'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {result.status}
                      </span>
                    </div>
                    
                    {result.status === 'success' ? (
                      <div className="text-sm text-gray-600 mt-1">
                        <p>Document ID: {result.document_id}</p>
                        <p>Chunks created: {result.chunks_created}</p>
                        <p>Size: {formatFileSize(result.file_size)}</p>
                      </div>
                    ) : (
                      <p className="text-sm text-red-600 mt-1">
                        Error: {result.error}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Next steps:</strong> Your uploaded documents are now available for AI queries. 
              The system will automatically search through them when relevant questions are asked.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};