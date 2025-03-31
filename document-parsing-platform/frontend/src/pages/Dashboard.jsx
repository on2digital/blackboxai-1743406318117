import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { FaCloudUploadAlt, FaSpinner } from 'react-icons/fa'

export default function Dashboard() {
  const [files, setFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)

  const onDrop = useCallback((acceptedFiles) => {
    setFiles(acceptedFiles.map(file => ({
      ...file,
      preview: URL.createObjectURL(file)
    })))
  }, [])

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
  })

  const handleUpload = async () => {
    setIsUploading(true)
    try {
      // TODO: Implement actual upload logic
      await new Promise(resolve => setTimeout(resolve, 2000))
      alert(`${files.length} files uploaded successfully!`)
      setFiles([])
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Document Upload</h1>
      
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
  )
}