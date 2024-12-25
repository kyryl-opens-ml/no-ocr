import { FileSearch, FolderPlus, Zap } from 'lucide-react';
import { Feature } from './Feature';

export function Features() {
  return (
    <div className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-blue-600">
            Powerful NoOCR
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need to search through your documents
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Our AI-powered search engine helps you find exactly what you're looking for across all your PDF documents, making information retrieval faster and more efficient than ever.
          </p>
        </div>
        
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            <Feature 
              icon={FolderPlus}
              title="Organize Cases"
              description="Create and manage collections of related PDFs. Keep your documents organized and easily accessible."
            />
            <Feature 
              icon={FileSearch}
              title="AI-Powered Search"
              description="Advanced semantic search capabilities help you find relevant information across all your documents instantly."
            />
            <Feature 
              icon={Zap}
              title="Lightning Fast"
              description="Get search results in milliseconds, no matter how large your document collection grows."
            />
          </dl>
        </div>
      </div>
    </div>
  );
}