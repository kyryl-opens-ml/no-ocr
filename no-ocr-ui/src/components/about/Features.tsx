import { FileSearch, FolderPlus, Zap } from 'lucide-react';
import { Feature } from './Feature';

/**
 * Features showcase the advanced RAG lifecycle as described in the Kyryl Opens ML blog post.
 * Emphasizes how our platform uses ColPali for vision-based retrieval,
 * LanceDB for robust embeddings storage, and Modal for GPU-powered workflows.
 */
export function Features() {
  return (
    <div className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-blue-600">
            Remove Complexity from Your RAG Applications
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Next-Generation Document &amp; Image Search
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Powered by ColPali for vision-driven retrieval and backed by LanceDB for lightning-fast vector search, our platform simplifies data ingestion and harnesses the power of advanced RAG technology for seamless PDF and image analysis.
          </p>
        </div>
        
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            <Feature 
              icon={FolderPlus}
              title="ColPali Vision Embeddings"
              description="Go beyond standard OCR. Harness powerful image embeddings for complex PDFs, charts, and infographics using ColPali to truly capture visual context."
            />
            <Feature 
              icon={FileSearch}
              title="RAG-First Platform"
              description="Combine intelligent textual retrieval with advanced (re)ranking and multi-modal analysis for robust query understanding, following the best practices in the 'Remove Complexity from Your RAG Applications' blog."
            />
            <Feature 
              icon={Zap}
              title="LanceDB-Powered Speed"
              description="Turbocharge your search with LanceDB vectors, enabling efficient storage and retrieval. Lightning-fast queries, minimal latency, all at scale."
            />
          </dl>
        </div>
      </div>
    </div>
  );
}