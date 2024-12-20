import { SearchResult } from '../../types/collection';

interface SearchResultsProps {
  results: SearchResult[];
}

export function SearchResults({ results }: SearchResultsProps) {
  if (results.length === 0) return null;

  return (
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
  );
}