import { useState, useEffect } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import axios from 'axios'
import { FaCopy, FaDownload, FaSearch } from 'react-icons/fa'
import SyntaxHighlighter from 'prism-react-renderer/prism'
import ErrorDisplay from '../components/ErrorDisplay'

const sampleData = {
  content: {
    text: "This is a sample extracted text from a document. It demonstrates how the parsed content will be displayed in the output interface.\n\nMultiple paragraphs are preserved in the output structure.",
    tables: [
      {
        header: ["Name", "Age", "Occupation"],
        rows: [
          ["John Doe", "32", "Software Engineer"],
          ["Jane Smith", "28", "Data Scientist"]
        ]
      }
    ],
    images: [
      {
        caption: "Sample diagram",
        url: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjxjaXJjbGUgY3g9IjEwMCIgY3k9IjEwMCIgcj0iODAiIGZpbGw9IiM0MjhkY2IiLz48L3N2Zz4="
      }
    ]
  },
  metadata: {
    filename: "sample-document.pdf",
    pages: 5,
    created: "2023-10-15T08:30:00Z",
    processed: "2023-10-16T14:45:00Z"
  }
}

export default function OutputPage() {
  const [outputFormat, setOutputFormat] = useState('json')
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredData, setFilteredData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const { documentId } = useParams()
  const location = useLocation()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        if (!documentId) {
          throw new Error('Invalid document ID')
        }
        
        const response = await axios.get(
          `${process.env.REACT_APP_API_BASE_URL}/results/${documentId}`,
          {
            validateStatus: (status) => status < 500
          }
        )

        if (response.data.status === 'completed') {
          setFilteredData({
            content: {
              text: response.data.content,
              tables: [], // Will be populated from actual data
              images: []  // Will be populated from actual data
            },
            metadata: response.data.metadata || {
              filename: 'document',
              pages: 1,
              created: new Date().toISOString(),
              processed: new Date().toISOString()
            }
          })
        } else {
          // Poll if still processing
          setTimeout(fetchData, 2000)
        }
      } catch (err) {
        setError(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [documentId, location.search])

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(filteredData, null, 2))
    alert('Output copied to clipboard!')
  }

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(filteredData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filteredData.metadata.filename.replace(/\.[^/.]+$/, '')}_output.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    // TODO: Implement actual search functionality
    alert(`Searching for: ${searchTerm}`)
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <ErrorDisplay error={error} onRetry={() => window.location.reload()} />
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Document Output</h1>
        <div className="flex space-x-3">
          <button
            onClick={() => setOutputFormat('json')}
            className={`px-3 py-1 rounded-md ${
              outputFormat === 'json' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
            }`}
          >
            JSON
          </button>
          <button
            onClick={() => setOutputFormat('xml')}
            className={`px-3 py-1 rounded-md ${
              outputFormat === 'xml' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
            }`}
          >
            XML
          </button>
        </div>
      </div>

      {filteredData && (
        <div className="space-y-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-medium text-gray-700 mb-3">Metadata</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Filename</p>
                <p className="font-medium">{filteredData.metadata.filename}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Pages</p>
                <p className="font-medium">{filteredData.metadata.pages}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Created</p>
                <p className="font-medium">
                  {new Date(filteredData.metadata.created).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Processed</p>
                <p className="font-medium">
                  {new Date(filteredData.metadata.processed).toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <form onSubmit={handleSearch} className="flex-1 max-w-md">
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search in document..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <FaSearch className="absolute left-3 top-3 text-gray-400" />
              </div>
            </form>
            <div className="flex space-x-2">
              <button
                onClick={handleCopy}
                className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                <FaCopy className="mr-2" />
                Copy
              </button>
              <button
                onClick={handleDownload}
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
              >
                <FaDownload className="mr-2" />
                Download
              </button>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-medium text-gray-700 mb-3">Content</h2>
            
            {outputFormat === 'json' ? (
              <div className="overflow-auto max-h-[600px]">
                <SyntaxHighlighter
                  language="javascript"
                  style={undefined}
                  customStyle={{ background: 'transparent' }}
                >
                  {JSON.stringify(filteredData.content, null, 2)}
                </SyntaxHighlighter>
              </div>
            ) : (
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-gray-500">XML output will be displayed here</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}