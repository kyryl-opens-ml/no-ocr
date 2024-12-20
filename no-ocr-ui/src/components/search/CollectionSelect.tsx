import { Collection } from '../../types/collection';

interface CollectionSelectProps {
  collections: Collection[];
  selectedCollection: string;
  onCollectionChange: (collectionId: string) => void;
}

export function CollectionSelect({
  collections,
  selectedCollection,
  onCollectionChange,
}: CollectionSelectProps) {
  return (
    <div>
      <label htmlFor="collection" className="block text-sm font-medium text-gray-700">
        Select Collection
      </label>
      <select
        id="collection"
        value={selectedCollection}
        onChange={(e) => onCollectionChange(e.target.value)}
        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        required
      >
        <option value="">Select a collection</option>
        {collections.map((collection) => (
          <option key={collection.id} value={collection.id}>
            {collection.name}
          </option>
        ))}
      </select>
    </div>
  );
}