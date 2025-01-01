import { BookOpen, Search, MessageSquare } from 'lucide-react';

/**
 * HowItWorks outlines our simplified RAG approach:
 * - Step 1: Upload & Process Complex PDFs (creates a "case")
 * - Step 2: We process your case and make it searchable
 * - Step 3: Ask any question, now using the latest open source vision models
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
            Our platform adopts a streamlined RAG approach. Simply create a case by uploading your PDFs, let us process them, then ask any question—even about visual elements—using best-in-class open source reasoning models.
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
                    Upload &amp; Process Complex PDFs
                  </h3>
                  <p className="mt-5 text-sm leading-6 text-gray-600">
                    Create a new case by uploading your most challenging PDF documents. Our system treats each PDF page carefully, generating embeddings without heavy OCR.
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
                    We Make It Searchable
                  </h3>
                  <p className="mt-5 text-sm leading-6 text-gray-600">
                    Once your case is processed, you can quickly run text-based queries to find relevant pages and references—no matter how intricate the PDF layout might be.
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
                    Ask Any Visual-Based Question
                  </h3>
                  <p className="mt-5 text-sm leading-6 text-gray-600">
                    Our approach quickly surfaces relevant pages, then a specialized open source vision model refines the final answer. Even if your PDFs have charts or diagrams, you’ll receive context-aware insights.
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