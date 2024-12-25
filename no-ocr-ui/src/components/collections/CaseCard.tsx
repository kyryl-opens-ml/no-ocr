import { FileText, Trash2 } from 'lucide-react';
import { Case } from '../../types/collection';
import { formatDate } from '../../utils/date';
import { useState } from 'react';
import { noOcrApiUrl } from '../../config/api';

interface CaseCardProps {
  caseItem: {
    name: string;
    status: string;
    number_of_PDFs: number;
    files: string[];
  };
}

export function CaseCard({ caseItem }: CaseCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this case?')) return;
    
    setIsDeleting(true);
    try {
      const response = await fetch(`${noOcrApiUrl}/delete_case/${caseItem.name}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete case');
      // Case will be removed from the list by the parent's useEffect
    } catch (error) {
      console.error('Error deleting case:', error);
      alert('Failed to delete case');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="relative group bg-white rounded-lg shadow-sm ring-1 ring-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center gap-x-3">
          <FileText className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">{caseItem.name}</h3>
        </div>
        
        <div className="mt-4 space-y-2">
          <p className="text-sm text-gray-600">Status: {caseItem.status}</p>
          <p className="text-sm text-gray-600">
            {caseItem.number_of_PDFs} PDF{caseItem.number_of_PDFs !== 1 ? 's' : ''}
          </p>
          <ul className="text-sm text-gray-500">
            {caseItem.files.map((file, index) => (
              <li key={index}>{file}</li>
            ))}
          </ul>
        </div>

        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Trash2 className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}