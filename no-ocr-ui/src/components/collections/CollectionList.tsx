import { useEffect, useState } from 'react';
import { Collection } from '../../types/collection';
import { CollectionCard } from './CollectionCard';
import { LoadingSpinner } from '../shared/LoadingSpinner';
import { EmptyState } from '../shared/EmptyState';
import { noOcrApiUrl } from '../../config/api';

export function CollectionList() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchCollections() {
      try {
        const response = await fetch(`${noOcrApiUrl}/get_collections`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        setCollections(data.collections || []);
      } catch (error) {
        console.error('Error fetching collections:', error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchCollections();
  }, []);

  if (isLoading) return <LoadingSpinner />;

  if (collections.length === 0) {
    return (
      <EmptyState
        title="No collections yet"
        description="Get started by creating your first collection"
        actionLink="/create-collection"
        actionText="Create Collection"
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {collections.map((collection) => (
        <CollectionCard key={collection.name} collection={collection} />
      ))}
    </div>
  );
}