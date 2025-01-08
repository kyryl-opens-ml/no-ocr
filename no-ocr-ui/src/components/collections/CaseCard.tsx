import { FileText, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { noOcrApiUrl } from '../../config/api';
import { Link } from 'react-router-dom';

interface CaseCardProps {
  caseItem: {
    name: string;
    status: string;
    number_of_PDFs: number;
    files: string[];
  };
}

export function CaseCard({ caseItem }: CaseCardProps) {
  const { user } = useAuthStore();
  const [isDeleting, setIsDeleting] = useState(false);
  const [apiMessage, setApiMessage] = useState<string | null>(null);
  const [status, setStatus] = useState(caseItem.status);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (status === 'processing') {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`${noOcrApiUrl}/get_case/${caseItem.name}?user_id=${user.id}`);
          const data = await response.json();
          setStatus(data.status);

          if (data.status === 'done' || data.status === 'error') {
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error fetching case status:', error);
        }
      }, 5000); // Poll every 5 seconds
    }

    return () => clearInterval(interval);
  }, [status, caseItem.name, user.id]);

  const handleDelete = async () => {
    // If not signed in, block the actual delete action:
    if (!user) {
      setApiMessage('You must be logged in to delete a case.');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this case?')) return;
    
    setIsDeleting(true);
    try {
      const response = await fetch(`${noOcrApiUrl}/delete_case/${caseItem.name}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete case');
      // The parent component (CaseList) will remove the case upon refresh
    } catch (error) {
      console.error('Error deleting case:', error);
      setApiMessage('Failed to delete case');
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'done':
        return 'text-green-600';
      case 'processing':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="relative group bg-white rounded-lg shadow-sm ring-1 ring-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center gap-x-3">
          <FileText className="h-6 w-6 text-blue-600" />
          <Link to={`/search?case=${caseItem.name}`} className="text-lg font-semibold text-gray-900 hover:underline">
            {caseItem.name}
          </Link>
        </div>
        
        <div className="mt-4 space-y-2">
          <p className="text-sm text-black flex items-center">
            Status: <span className={getStatusColor()}> {status}</span> 
            {status === 'processing' && (
              <svg className="animate-spin ml-2 h-5 w-5 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
            )}
          </p>
          <p className="text-sm text-gray-600">
            {caseItem.number_of_PDFs} PDF{caseItem.number_of_PDFs !== 1 ? 's' : ''}
          </p>
          <ul className="text-sm text-gray-500">
            {caseItem.files.map((file, index) => (
              <li key={index}>{file}</li>
            ))}
          </ul>
        </div>

        {user && (
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="absolute top-4 right-4 p-2 text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        )}

        {apiMessage && (
          <div className="mt-4 p-4 bg-gray-100 rounded-md">
            <p className="text-sm text-gray-700">{apiMessage}</p>
          </div>
        )}
      </div>
    </div>
  );
}