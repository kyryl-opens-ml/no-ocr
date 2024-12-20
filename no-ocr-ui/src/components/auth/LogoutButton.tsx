import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { supabase } from '../../lib/supabase';

export function LogoutButton() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/login');
  };

  return (
    <button
      onClick={handleLogout}
      className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-500 hover:text-gray-700"
    >
      <LogOut className="w-5 h-5 mr-2" />
      Logout
    </button>
  );
}