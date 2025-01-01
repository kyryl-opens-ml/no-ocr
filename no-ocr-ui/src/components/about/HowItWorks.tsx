import { BookOpen, Search, MessageSquare } from 'lucide-react';

/**
 * HowItWorks introduces the RAG workflow with references to
 * the "Remove Complexity from Your RAG Applications" approach.
 * Emphasizes ColPali-based PDFs as images, LanceDB for embeddings,
 * and an LLM for final Q&A.
 */
export function HowItWorks() {
  return (
    <div className="bg-white py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:max-w-4xl">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Our platform adopts the multi-modal RAG approach highlighted by Kyryl Opens ML, leveraging ColPali for rich PDF page embeddings and LanceDB for straightforward vector management. We’ve packaged everything with Modal for easy GPU access and advanced pipeline orchestration.
          </p>
          
          <div className="mt-16 space-y-20 lg:mt-20 lg:space-y-20">
            <article className="relative isolate flex flex-col gap-8 lg:flex-row">
              <div className="relative aspect-[16/9] sm:aspect-[2/1] lg:aspect-square lg:w-64 lg:shrink-0">
                <BookOpen className="absolute inset-0 h-full w-full text-gray-900" />
              </div>
              <div>
                <div className="flex items-center gap-x-4 text-xs">
                  <time dateTime="2024" className="text-gray-500">
                    Step 1
                  </time>
                </div>
                <div className="group relative max-w-xl">
                  <h3 className="mt-3 text-lg font-semibold leading-6 text-gray-900">
                    Upload &amp; Process Complex PDFs or Images
                  </h3>
                  <p className="mt-5 text-sm leading-6 text-gray-600">
                    We ingest your PDF files—no matter how visually dense—by treating each page like an image. ColPali converts it into embeddings, ready for indexing in LanceDB. This eliminates the need for heavy OCR pipelines.
                  </p>
                </div>
              </div>
            </article>

            <article className="relative isolate flex flex-col gap-8 lg:flex-row">
              <div className="relative aspect-[16/9] sm:aspect-[2/1] lg:aspect-square lg:w-64 lg:shrink-0">
                <Search className="absolute inset-0 h-full w-full text-gray-900" />
              </div>
              <div>
                <div className="flex items-center gap-x-4 text-xs">
                  <time dateTime="2024" className="text-gray-500">
                    Step 2
                  </time>
                </div>
                <div className="group relative max-w-xl">
                  <h3 className="mt-3 text-lg font-semibold leading-6 text-gray-900">
                    Vector Storage &amp; Retrieval
                  </h3>
                  <p className="mt-5 text-sm leading-6 text-gray-600">
                    We store your document embeddings in LanceDB, offering efficient vector search with minimal overhead. This handles both text-based and vision-based embeddings for advanced multi-modal queries.
                  </p>
                </div>
              </div>
            </article>

            <article className="relative isolate flex flex-col gap-8 lg:flex-row">
              <div className="relative aspect-[16/9] sm:aspect-[2/1] lg:aspect-square lg:w-64 lg:shrink-0">
                <MessageSquare className="absolute inset-0 h-full w-full text-gray-900" />
              </div>
              <div>
                <div className="flex items-center gap-x-4 text-xs">
                  <time dateTime="2024" className="text-gray-500">
                    Step 3
                  </time>
                </div>
                <div className="group relative max-w-xl">
                  <h3 className="mt-3 text-lg font-semibold leading-6 text-gray-900">
                    Final AI Q&amp;A
                  </h3>
                  <p className="mt-5 text-sm leading-6 text-gray-600">
                    For each user query, our multi-modal approach quickly surfaces relevant pages, images, and text, then a specialized LLM (e.g., Phi3.5-vision) refines the final answer. The result: a streamlined, context-aware Q&amp;A experience.
                  </p>
                </div>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
  );
}