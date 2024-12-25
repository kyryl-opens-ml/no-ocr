import React, { useState, useEffect } from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { Collection } from '../types/collection';
import { noOcrApiUrl } from '../config/api';

export default function Search() {
  const [selectedCollection, setSelectedCollection] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [answers, setAnswers] = useState<{ [key: number]: { is_answer: boolean, answer: string } }>({});

  const [collections, setCollections] = useState<Collection[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalImage, setModalImage] = useState('');

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
    setResults([]);
    setAnswers({});

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

      data.search_results.forEach((result: any, index: number) => {
        fetchAnswer(searchQuery, selectedCollection, result.pdf_name, result.pdf_page)
          .then(answer => {
            setAnswers(prevAnswers => ({ ...prevAnswers, [index]: answer }));
          });
      });
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const fetchAnswer = async (userQuery: string, collectionName: string, pdfName: string, pdfPage: number) => {
    try {
      const response = await fetch(`${noOcrApiUrl}/vllm_call`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: new URLSearchParams({
          user_query: userQuery,
          collection_name: collectionName,
          pdf_name: pdfName,
          pdf_page: pdfPage.toString(),
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Fetching answer failed:', error);
      return { is_answer: false, answer: 'NA' };
    }
  };

  const openModal = (imageBase64: string) => {
    setModalImage(imageBase64);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setModalImage('');
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">AI Search</h1>
      
      <form onSubmit={handleSearch} className="space-y-4">
        <div>
          <label htmlFor="collection" className="block text-sm font-medium text-gray-700">
            Select Collection
          </label>
          <div className="relative">
            <select
              id="collection"
              value={selectedCollection}
              onChange={(e) => setSelectedCollection(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 appearance-none bg-white py-2 px-3 pr-8"
              required
            >
              <option value="">Select a collection</option>
              {collections.map((collection) => (
                <option key={collection.id} value={collection.id}>
                  {collection.name}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
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
          <h2 className="text-2xl font-bold text-blue-900 mb-6">Search Results</h2>
          <div className="grid grid-cols-1 gap-6">
            {results.map((result, index) => (
              <div key={index} className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-xl shadow-lg border border-blue-200 grid grid-cols-3 gap-6">
                <div className="col-span-2">
                  <img
                    src={`data:image/jpeg;base64,${result.image_base64}`}
                    alt={`Page ${result.pdf_page} of ${result.pdf_name}`}
                    className="w-full h-auto rounded-lg border border-blue-300 cursor-pointer"
                    onClick={() => openModal(result.image_base64)}
                  />
                </div>
                <div className="flex flex-col justify-between">
                  <div className="bg-blue-50 p-5 rounded-xl shadow-md border border-blue-200">
                    <h3 className="font-semibold text-blue-800 text-lg">
                      Document Name: <span className="text-blue-600">{result.pdf_name}</span>
                    </h3>
                  </div>
                  <div className="bg-blue-50 p-5 rounded-xl shadow-md border border-blue-200 mt-2">
                    <p className="text-md text-blue-700">
                      Page: <span className="font-semibold">{result.pdf_page}</span>
                    </p>
                  </div>
                  <div className="bg-blue-50 p-5 rounded-xl shadow-md border border-blue-200 mt-2">
                    <p className="text-md text-blue-700">
                      Score: <span className="font-semibold">{result.score.toFixed(2)}</span>
                    </p>
                  </div>
                  <div className="bg-blue-50 p-5 rounded-xl shadow-md border border-blue-200 mt-2">
                    <h3 className="font-semibold text-blue-800">Does it Answer:</h3>
                    <p className="mt-2 text-md text-blue-700">
                      {answers[index] ? (answers[index].is_answer ? 'Yes' : 'No') : 'Loading...'}
                    </p>
                  </div>
                  <div className="bg-blue-50 p-5 rounded-xl shadow-md border border-blue-200 mt-2">
                    <h3 className="font-semibold text-blue-800">Answer:</h3>
                    <p className="mt-2 text-md text-blue-700">
                      {answers[index] ? answers[index].answer : 'Loading...'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded-lg shadow-lg">
            <button onClick={closeModal} className="text-red-500">Close</button>
            <img src={`data:image/jpeg;base64,${modalImage}`} alt="Enlarged view" className="w-full h-auto mt-4" />
          </div>
        </div>
      )}
    </div>
  );
}
