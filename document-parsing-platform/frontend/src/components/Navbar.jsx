import { Link, useLocation } from 'react-router-dom'
import { FaFileAlt, FaCog, FaTable } from 'react-icons/fa'

export default function Navbar() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', icon: <FaFileAlt />, label: 'Documents' },
    { path: '/configure', icon: <FaCog />, label: 'Configuration' },
    { path: '/output', icon: <FaTable />, label: 'Output' }
  ]

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <span className="text-xl font-semibold text-gray-800">
              Document Parser
            </span>
          </div>
          <div className="flex space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  location.pathname === item.path
                    ? 'border-blue-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}