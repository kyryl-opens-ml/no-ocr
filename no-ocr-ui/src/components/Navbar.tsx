import { FileSearch, FolderPlus } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { LogoutButton } from './auth/LogoutButton';
import { useAuthStore } from '../stores/authStore';

export default function Navbar() {
  const location = useLocation();
  const { user } = useAuthStore();
  
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            <Link 
              to="/" 
              className="flex items-center text-xl font-semibold text-gray-900"
            >
              PDF Search
            </Link>
            
            <div className="flex space-x-4">
              <Link
                to="/create-collection"
                className={`inline-flex items-center px-3 py-2 text-sm font-medium ${
                  location.pathname === '/create-collection'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <FolderPlus className="w-5 h-5 mr-2" />
                Create Collection
              </Link>
              
              <Link
                to="/search"
                className={`inline-flex items-center px-3 py-2 text-sm font-medium ${
                  location.pathname === '/search'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <FileSearch className="w-5 h-5 mr-2" />
                AI Search
              </Link>
            </div>
          </div>
          
          {user && (
            <div className="flex items-center">
              <span className="text-sm text-gray-500 mr-4">{user.email}</span>
              <LogoutButton />
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}