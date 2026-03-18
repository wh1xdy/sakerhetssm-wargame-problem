'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

function NewPoemFormInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');

  // Pre-populate form if returning from preview
  useEffect(() => {
    const titleParam = searchParams.get('title');
    const bodyParam = searchParams.get('body');
    if (titleParam) setTitle(titleParam);
    if (bodyParam) setBody(bodyParam);
  }, [searchParams]);

  const handlePreview = () => {
    // Navigate to preview page with query parameters
    const params = new URLSearchParams();
    params.set('title', title || 'Untitled Poem');
    params.set('body', body || 'No content provided.');

    const url = `/poems/preview?${params.toString()}`;
    router.push(url);
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-8">
          <header className="mb-8">
            <h1 className="text-4xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">
              Preview Your Poem
            </h1>
            <p className="text-lg text-zinc-600 dark:text-zinc-400">
              Fill in the form below to see how your poem would appear. You can use Markdown formatting in the body.
            </p>
          </header>

          <div className="space-y-6">
            <div>
              <label
                htmlFor="title"
                className="block text-sm font-semibold mb-2 text-zinc-900 dark:text-zinc-100"
              >
                Poem Title
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter your poem title..."
                className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-500"
              />
            </div>

            <div>
              <label
                htmlFor="body"
                className="block text-sm font-semibold mb-2 text-zinc-900 dark:text-zinc-100"
              >
                Poem Body (Markdown supported)
              </label>
              <textarea
                id="body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="# Your Poem Title&#10;&#10;Write your poem here...&#10;&#10;You can use **bold**, *italic*, and other Markdown formatting."
                rows={12}
                className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-500 font-mono text-sm"
              />
              <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                Tip: Use Markdown syntax like # for headings, ** for bold, * for italic
              </p>
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={handlePreview}
                className="flex-1 px-6 py-3 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg hover:bg-zinc-700 dark:hover:bg-zinc-300 transition-colors font-semibold"
              >
                Preview Poem
              </button>
              <Link
                href="/"
                className="inline-flex items-center justify-center px-6 py-3 bg-zinc-200 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors font-semibold"
              >
                Cancel
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function NewPoemForm() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-zinc-50 dark:bg-black py-12 px-4 flex items-center justify-center">
        <div className="text-zinc-600 dark:text-zinc-400">Loading...</div>
      </div>
    }>
      <NewPoemFormInner />
    </Suspense>
  );
}
