'use client';

import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { evaluate } from '@mdx-js/mdx';
import * as runtime from 'react/jsx-runtime';
import remarkGfm from 'remark-gfm';

export default function PreviewClient() {
  const searchParams = useSearchParams();
  const title = searchParams.get('title') || 'Untitled Poem';
  const body = searchParams.get('body') || '# Untitled Poem\n\nNo content provided.';
  const [MDXContent, setMDXContent] = useState<any>(null);

  useEffect(() => {
    const compileMDX = async () => {
      try {
        const { default: Content } = await evaluate(body, {
          ...runtime,
          remarkPlugins: [remarkGfm],
        });
        setMDXContent(() => Content);
      } catch (error) {
        console.error('MDX compilation error:', error);
        setMDXContent(() => () => <><div className="text-red-600">CSP violation, showing raw content instead</div><div>{body}</div></>);
      }
    };

    compileMDX();
  }, [body]);

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black py-12 px-4">
      <article className="max-w-3xl mx-auto bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-8">
        <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Preview Mode:</strong> This is how your poem would appear. Go back to edit or start over.
          </p>
        </div>

        <header className="mb-8 border-b border-zinc-200 dark:border-zinc-700 pb-6">
          <h1 className="text-4xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">
            {title}
          </h1>
          <p className="text-xl text-zinc-600 dark:text-zinc-400">
            by Anonymous
          </p>
        </header>

        <div className="prose prose-zinc dark:prose-invert max-w-none">
          {MDXContent ? <MDXContent /> : <div className="text-zinc-400">Loading preview...</div>}
        </div>

        <div className="mt-8 pt-6 border-t border-zinc-200 dark:border-zinc-700 flex gap-4">
          <Link
            href={`/poems/new?${searchParams.toString()}`}
            className="inline-block px-6 py-3 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg hover:bg-zinc-700 dark:hover:bg-zinc-300 transition-colors"
          >
            ← Edit Poem
          </Link>
          <Link
            href="/"
            className="inline-block px-6 py-3 bg-zinc-200 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </article>
    </div>
  );
}
