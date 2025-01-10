import { FileSearch } from 'lucide-react';
import { Link } from 'react-router-dom';

/**
 * Hero showcases the main application's document-oriented RAG features
 * and invites users to explore our advanced AI search.
 */
export function Hero() {
  return (
    <div className="relative isolate overflow-hidden bg-white">
      <svg
        className="absolute inset-0 -z-10 h-full w-full stroke-gray-200 [mask-image:radial-gradient(100%_100%_at_top_right,white,transparent)]"
        aria-hidden="true"
      >
        <defs>
          <pattern
            id="0787a7c5-978c-4f66-83c7-11c213f99cb7"
            width={200}
            height={200}
            x="50%"
            y={-1}
            patternUnits="userSpaceOnUse"
          >
            <path d="M.5 200V.5H200" fill="none" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" strokeWidth={0} fill="url(#0787a7c5-978c-4f66-83c7-11c213f99cb7)" />
      </svg>
      <div className="mx-auto max-w-7xl px-6 pb-24 pt-10 sm:pb-32 lg:flex lg:px-8 lg:py-40">
        <div className="mx-auto max-w-2xl lg:mx-0 lg:max-w-xl lg:flex-shrink-0 lg:pt-8">
          <div className="mt-24 sm:mt-32 lg:mt-16">
            <Link to="/" className="inline-flex space-x-6">
              <span className="rounded-full bg-blue-600/10 px-3 py-1 text-sm font-semibold leading-6 text-blue-600 ring-1 ring-inset ring-blue-600/10">
                Latest Features
              </span>
              <span className="inline-flex items-center space-x-2 text-sm font-medium leading-6 text-gray-600">
                <span>Document-First RAG</span>
              </span>
            </Link>
          </div>
          <h1 className="mt-10 text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            Intelligent Document Search with RAG
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Explore an end-to-end solution for complex PDFs, powered by ColPali embeddings. Our AI understands 
            your documents’ deep structure—making retrieval truly comprehensive.
          </p>
          <div className="mt-10 flex items-center gap-x-6">
            <Link
              to="/register"
              className="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Get started
            </Link>
            <Link to="/search" className="text-sm font-semibold leading-6 text-gray-900">
              Try AI Search <span aria-hidden="true">→</span>
            </Link>
          </div>
        </div>
        <div className="mx-auto mt-16 flex max-w-2xl sm:mt-24 lg:ml-10 lg:mr-0 lg:mt-0 lg:max-w-none lg:flex-none xl:ml-32">
          <div className="max-w-3xl flex-none sm:max-w-5xl lg:max-w-none">
            <div className="-m-2 rounded-xl bg-gray-900/5 p-2 ring-1 ring-inset ring-gray-900/10 lg:-m-4 lg:rounded-2xl lg:p-4">
              <div className="w-[28rem] rounded-md bg-white p-8 shadow-2xl ring-1 ring-gray-900/10">
                <div className="flex items-center gap-4">
                  <FileSearch className="h-8 w-8 text-blue-600" />
                  <h2 className="text-lg font-semibold">AI-Assisted Search</h2>
                </div>
                <p className="mt-4 text-sm text-gray-600">
                  "Find all relevant references discussing inference costs in 2023 PDF reports."
                </p>
                <div className="mt-6 flex gap-4">
                  <div className="flex-1 rounded-lg bg-gray-100 px-4 py-3">
                    <div className="h-2 w-3/4 rounded-full bg-gray-200"></div>
                  </div>
                  <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white">
                    Search
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>  
    </div>
  );
}