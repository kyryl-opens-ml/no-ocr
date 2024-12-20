import { useEffect, useState } from 'react';
import { Collection } from '../../types/collection';
import { CollectionCard } from './CollectionCard';
import { LoadingSpinner } from '../shared/LoadingSpinner';
import { EmptyState } from '../shared/EmptyState';
import { supabase } from '../../lib/supabase';

export function CollectionList() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchCollections() {
      try {
        const { data, error } = await supabase
          .from('collections')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;
        setCollections(data || []);
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
        <CollectionCard key={collection.id} collection={collection} />
      ))}
    </div>
  );
}