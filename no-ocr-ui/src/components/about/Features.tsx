import { FileSearch, FolderPlus, Zap, Layers } from 'lucide-react';
import { Feature } from './Feature';

/**
 * Features showcase the simplified RAG lifecycle.
 * Removes direct mentions of images or LanceDB,
 * adds open source and multi-case features.
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
            Next-Generation Document Search
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Powered by ColPali for document-focused retrieval, our platform simplifies data ingestion 
            and harnesses advanced RAG technology for seamless PDF analysis.
          </p>
        </div>

        {/* 
          Updated to four features, removing references to image or LanceDB speed,
          adding open source and multi-case features. 
        */}
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-4">
            <Feature 
              icon={FolderPlus}
              title="ColPali Document Embeddings"
              description="Go beyond standard OCR. Harness powerful embeddings for complex PDFs to truly capture important context."
            />
            <Feature 
              icon={FileSearch}
              title="RAG-First Platform"
              description="Combine intelligent textual retrieval with advanced ranking for robust query understanding, following best practices in modern RAG systems."
            />
            <Feature 
              icon={Zap}
              title="Open Source & Self-Hosting"
              description="Your data remains secure. Easily self-host our platform and adapt it to your infrastructure — no vendor lock-in."
            />
            <Feature 
              icon={Layers}
              title="Multiple Cases at Once"
              description="Seamlessly work on several document cases in parallel, keeping ingestion and search workflows efficient and organized."
            />
          </dl>
        </div>
      </div>
    </div>
  );
}