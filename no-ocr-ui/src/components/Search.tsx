import React, { useState, useEffect } from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { Collection } from '../types/collection';
import { noOcrApiUrl } from '../config/api';

export default function Search() {
  const [selectedCollection, setSelectedCollection] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const [collections, setCollections] = useState<Collection[]>([]);
  
  useEffect(() => {
    async function fetchCollections() {
      try {
        const response = await fetch(`${noOcrApiUrl}/get_collections`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        setCollections(data.collections || []);
      } catch (error) {
        console.error('Error fetching collections:', error);
      }
    }

    fetchCollections();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCollection || !searchQuery) return;

    setIsSearching(true);
    try {
      const response = await fetch(`${noOcrApiUrl}/search`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: new URLSearchParams({
          user_query: searchQuery,
          collection_name: selectedCollection,
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setResults(data.search_results || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
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
                <h3 className="font-medium text-gray-900">
                  PDF: {result.pdf_name}
                </h3>
                <p className="mt-1 text-sm text-gray-600">
                  Page {result.pdf_page}
                </p>
                <p className="mt-2 text-gray-700">
                  {result.llm_interpretation}
                </p>
                <div className="mt-2 text-sm text-gray-500">
                  Score: {result.score.toFixed(2)}
                </div>
                <div className="mt-2">
                  <img
                    src={`data:image/jpeg;base64,${result.image_base64}`}
                    alt={`Page ${result.pdf_page} of ${result.pdf_name}`}
                    className="w-full h-auto rounded-md max-w-xs"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
