import { useState, useRef } from 'react'
import { Upload, File, CheckCircle, AlertCircle, X } from 'lucide-react'

interface DocumentUploadProps {
  onUploadSuccess?: (filename: string) => void
  onClose?: () => void
}

const DocumentUpload = ({ onUploadSuccess, onClose }: DocumentUploadProps) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [uploadMessage, setUploadMessage] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown']
    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.md')) {
      setUploadStatus('error')
      setUploadMessage('Please upload a PDF or TXT file')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setUploadStatus('error')
      setUploadMessage('File size must be less than 10MB')
      return
    }

    setIsUploading(true)
    setUploadStatus('idle')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/upload-document', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        setUploadStatus('success')
        setUploadMessage(`Successfully uploaded "${file.name}"`)
        onUploadSuccess?.(file.name)
      } else {
        const error = await response.json()
        setUploadStatus('error')
        setUploadMessage(error.detail || 'Upload failed')
      }
    } catch (error) {
      setUploadStatus('error')
      setUploadMessage('Network error. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full m-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Upload Document</h2>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
          )}
        </div>

        <div className="p-6">
          <div
            className={`
              border-2 border-dashed rounded-lg p-8 text-center transition-colors
              ${isDragging 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-300 hover:border-gray-400'
              }
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center">
              {isUploading ? (
                <>
                  <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4"></div>
                  <p className="text-gray-600">Uploading document...</p>
                </>
              ) : (
                <>
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Drop your document here
                  </p>
                  <p className="text-gray-600 mb-4">
                    or{' '}
                    <button
                      onClick={handleBrowseClick}
                      className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                      browse files
                    </button>
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports PDF and TXT files (max 10MB)
                  </p>
                </>
              )}
            </div>
          </div>

          {uploadStatus !== 'idle' && (
            <div
              className={`
                mt-4 p-4 rounded-lg flex items-start space-x-3
                ${uploadStatus === 'success' 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-red-50 border border-red-200'
                }
              `}
            >
              {uploadStatus === 'success' ? (
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <p
                  className={`
                    text-sm font-medium
                    ${uploadStatus === 'success' ? 'text-green-800' : 'text-red-800'}
                  `}
                >
                  {uploadStatus === 'success' ? 'Upload Successful' : 'Upload Failed'}
                </p>
                <p
                  className={`
                    text-sm
                    ${uploadStatus === 'success' ? 'text-green-700' : 'text-red-700'}
                  `}
                >
                  {uploadMessage}
                </p>
              </div>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {uploadStatus === 'success' && (
          <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
            <button onClick={onClose} className="btn-primary">
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload