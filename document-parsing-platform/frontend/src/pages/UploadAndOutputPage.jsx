import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { 
  FaCloudUploadAlt, 
  FaSpinner, 
  FaCheckCircle, 
  FaTimesCircle, 
  FaSignInAlt 
} from 'react-icons/fa';
import SyntaxHighlighter from 'prism-react-renderer/prism';

export default function UploadAndOutputPage() {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [outputData, setOutputData] = useState(null);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/api/auth/login`,
        { email, password }
      );
      localStorage.setItem('token', response.data.token);
      setToken(response.data.token);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    setFiles(acceptedFiles.map(file => ({
      ...file,
      preview: URL.createObjectURL(file),
      status: 'pending'
    })));
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.txt']
    },
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const handleUpload = async () => {
    if (!token) {
      setError('Please login first');
      return;
    }

    setIsUploading(true);
    setProcessingStatus('uploading');
    
    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/api/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setProcessingStatus('processing');
      if (response.data.documentId) {
        pollForResults(response.data.documentId);
      } else {
        throw new Error('Upload failed');
      }
    } catch (err) {
      setError(err);
      setProcessingStatus('error');
      setIsUploading(false);
    }
  };

  const pollForResults = async (documentId) => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_BASE_URL}/results/${documentId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.status === 'completed') {
        setOutputData(response.data);
        setProcessingStatus('completed');
      } else if (response.data.status === 'processing') {
        setTimeout(() => pollForResults(documentId), 2000);
      } else {
        setError(new Error('Processing failed'));
        setProcessingStatus('error');
      }
    } catch (err) {
      setError(err);
      setProcessingStatus('error');
    } finally {
      setIsUploading(false);
    }
  };

  const getStatusIcon = () => {
    switch (processingStatus) {
      case 'uploading':
        return <FaSpinner className="animate-spin text-blue-500" />;
      case 'processing':
        return <FaSpinner className="animate-spin text-yellow-500" />;
      case 'completed':
        return <FaCheckCircle className="text-green-500" />;
      case 'error':
        return <FaTimesCircle className="text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
      {/* Upload Section */}
      <div className="space-y-6">
        {!token ? (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Login Required</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={handleLogin}
                className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center justify-center"
              >
                <FaSignInAlt className="mr-2" />
                Login
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-800">Upload Documents</h1>
            
            <div 
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
              }`}
            >
              <input {...getInputProps()} />
              <FaCloudUploadAlt className="mx-auto text-4xl text-gray-400 mb-3" />
              <p className="text-gray-600">
                {isDragActive ? (
                  'Drop your documents here'
                ) : (
                  'Drag & drop files here, or click to select files'
                )}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supported formats: PDF, DOCX, XLSX, TXT, JPG, PNG, TIFF
              </p>
            </div>

            {files.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-lg font-medium text-gray-700">Selected Files ({files.length})</h2>
                <ul className="divide-y divide-gray-200 border rounded-lg">
                  {files.map((file, index) => (
                    <li key={index} className="p-3 flex justify-between items-center">
                      <div>
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <button 
                        onClick={() => setFiles(files.filter((_, i) => i !== index))}
                        className="text-red-500 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className={`w-full py-2 px-4 rounded-md text-white font-medium ${
                    isUploading ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                >
                  {isUploading ? (
                    <span className="flex items-center justify-center">
                      <FaSpinner className="animate-spin mr-2" />
                      Uploading...
                    </span>
                  ) : (
                    'Process Documents'
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Output Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">Document Output</h1>
          {processingStatus && (
            <div className="flex items-center space-x-2">
              {getStatusIcon()}
              <span className="capitalize">
                {processingStatus === 'uploading' && 'Uploading files...'}
                {processingStatus === 'processing' && 'Processing documents...'}
                {processingStatus === 'completed' && 'Processing complete!'}
                {processingStatus === 'error' && 'Processing error'}
              </span>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <FaTimesCircle className="h-5 w-5 text-red-500" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  {error.message || 'An error occurred during processing'}
                </p>
              </div>
            </div>
          </div>
        )}

        {outputData && (
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-lg font-medium text-gray-700 mb-3">Metadata</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Filename</p>
                  <p className="font-medium">{outputData.metadata.filename}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Pages</p>
                  <p className="font-medium">{outputData.metadata.pages}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-lg font-medium text-gray-700 mb-3">Content</h2>
              <div className="overflow-auto max-h-[600px]">
                <SyntaxHighlighter
                  language="javascript"
                  style={undefined}
                  customStyle={{ background: 'transparent' }}
                >
                  {JSON.stringify(outputData.content, null, 2)}
                </SyntaxHighlighter>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}