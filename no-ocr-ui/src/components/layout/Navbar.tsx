import { FileSearch, FolderPlus, Info, Library } from 'lucide-react';
import { Link } from 'react-router-dom';
import { LogoutButton } from '../auth/LogoutButton';
import { useAuthStore } from '../../stores/authStore';
import { NavLink } from './NavLink';

export default function Navbar() {
  const { user } = useAuthStore();
  
  return (
    <nav className="bg-background shadow-md">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            <Link 
              to="/" 
              className="flex items-center text-xl font-heading text-secondary"
            >
              NoOCR
            </Link>
            
            <div className="flex space-x-4">
              <NavLink 
                to="/search" 
                icon={<FileSearch className="w-5 h-5 mr-2" />}
                label="AI Search"
              />
              <NavLink 
                to="/create-case" 
                icon={<FolderPlus className="w-5 h-5 mr-2" />}
                label="Create Case"
              />
              <NavLink 
                to="/cases" 
                icon={<Library className="w-5 h-5 mr-2" />}
                label="Cases"
              />
              
              <NavLink 
                to="/about" 
                icon={<Info className="w-5 h-5 mr-2" />}
                label="About"
              />
            </div>
          </div>
          
          <div className="flex items-center">
            {user ? (
              <>
                <span className="text-sm text-gray-500 mr-4">{user.email}</span>
                <LogoutButton />
              </>
            ) : (
              <div className="flex space-x-4">
                <Link
                  to="/login"
                  className="text-gray-500 hover:text-gray-700 px-3 py-2 text-sm font-medium"
                >
                  Sign in
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 text-white hover:bg-blue-500 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Sign up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}