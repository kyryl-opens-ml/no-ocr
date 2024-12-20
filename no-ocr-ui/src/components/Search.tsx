import React, { useState } from 'react';
import { Search as SearchIcon } from 'lucide-react';

export default function Search() {
  const [selectedCollection, setSelectedCollection] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Mock collections - replace with actual data
  const collections = [
    { id: '1', name: 'Research Papers' },
    { id: '2', name: 'Technical Documentation' },
  ];

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCollection || !searchQuery) return;

    setIsSearching(true);
    try {
      // TODO: Implement your search API call here
      // const response = await searchPDFs(selectedCollection, searchQuery);
      // setResults(response.results);
      
      // Mock results
      setTimeout(() => {
        setResults([
          {
            documentName: 'example.pdf',
            excerpt: 'Relevant text excerpt...',
            relevanceScore: 0.95,
            pageNumber: 1
          }
        ]);
        setIsSearching(false);
      }, 1000);
    } catch (error) {
      console.error('Search failed:', error);
      setIsSearching(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">AI Search</h1>
      
      <form onSubmit={handleSearch} className="space-y-4">
        <div>
          <label htmlFor="collection" className="block text-sm font-medium text-gray-700">
            Select Collection
          </label>
          <select
            id="collection"
            value={selectedCollection}
            onChange={(e) => setSelectedCollection(e.target.value)}
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

        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Enter your search query..."
            className="block w-full rounded-md border-gray-300 pl-10 pr-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            required
          />
          <SearchIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
        </div>

        <button
          type="submit"
          disabled={isSearching || !selectedCollection || !searchQuery}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Results</h2>
          <div className="space-y-4">
            {results.map((result, index) => (
              <div
                key={index}
                className="bg-white p-4 rounded-lg shadow-sm border border-gray-200"
              >
                <h3 className="font-medium text-gray-900">{result.documentName}</h3>
                <p className="mt-1 text-sm text-gray-600">Page {result.pageNumber}</p>
                <p className="mt-2 text-gray-700">{result.excerpt}</p>
                <div className="mt-2 text-sm text-gray-500">
                  Relevance: {(result.relevanceScore * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}