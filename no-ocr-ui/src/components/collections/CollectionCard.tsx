import { FileText, Trash2 } from 'lucide-react';
import { Collection } from '../../types/collection';
import { formatDate } from '../../utils/date';
import { useState } from 'react';
import { noOcrApiUrl } from '../../config/api';

interface CollectionCardProps {
  collection: Collection;
}

export function CollectionCard({ collection }: CollectionCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this collection?')) return;
    
    setIsDeleting(true);
    try {
      const response = await fetch(`${noOcrApiUrl}/delete_collection/${collection.name}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete collection');
      // Collection will be removed from the list by the parent's useEffect
    } catch (error) {
      console.error('Error deleting collection:', error);
      alert('Failed to delete collection');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="relative group bg-white rounded-lg shadow-sm ring-1 ring-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center gap-x-3">
          <FileText className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">{collection.name}</h3>
        </div>
        
        <div className="mt-4 space-y-2">
          <p className="text-sm text-gray-600">
            {collection.documentCount} document{collection.documentCount !== 1 ? 's' : ''}
          </p>
          <p className="text-sm text-gray-500">
            Created {formatDate(collection.createdAt)}
          </p>
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