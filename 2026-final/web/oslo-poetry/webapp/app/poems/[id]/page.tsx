import { MDXRemote } from 'next-mdx-remote/rsc';
import remarkGfm from 'remark-gfm';
import { notFound } from 'next/navigation';
import { Suspense } from 'react';
import PreviewClient from './PreviewClient';

// Sample poems data - replace this with your actual data source
const poems: Record<string, { title: string; content: string; author?: string }> = {
  'the-raven': {
    title: 'The Raven',
    author: 'Edgar Allan Poe',
    content: `# The Raven

Once upon a midnight dreary, while I pondered, weak and weary,
Over many a quaint and curious volume of forgotten lore—
While I nodded, nearly napping, suddenly there came a tapping,
As of some one gently rapping, rapping at my chamber door.
"'Tis some visitor," I muttered, "tapping at my chamber door—
Only this and nothing more."

## Analysis

This famous narrative poem was first published in 1845. The poem is noted for its musicality, stylized language, and supernatural atmosphere.`
  },
  'the-bells': {
    title: 'The Bells',
    author: 'Edgar Allan Poe',
    content: `# The Bells

**Hear the sledges with the bells—**
Silver bells!
What a world of merriment their melody foretells!
How they tinkle, tinkle, tinkle,
In the icy air of night!

## Overview

"The Bells" is a heavily onomatopoetic poem by Edgar Allan Poe which was not published until after his death in 1849.`
  }
};

interface PageProps {
  params: Promise<{
    id: string;
  }>;
  searchParams: Promise<{
    title?: string;
    body?: string;
  }>;
}

export default async function PoemPage({ params, searchParams }: PageProps) {
  const { id } = await params;
  const queryParams = await searchParams;

  // Check if query parameters exist for preview mode
  const hasQueryParams = queryParams.title || queryParams.body;

  if (hasQueryParams) {
    // Preview mode - render client component
    return (
      <Suspense fallback={<div className="min-h-screen bg-zinc-50 dark:bg-black py-12 px-4 flex items-center justify-center">
        <div className="text-zinc-600 dark:text-zinc-400">Loading preview...</div>
      </div>}>
        <PreviewClient />
      </Suspense>
    );
  }

  // Normal mode - look up existing poem
  const poem = poems[id];

  // Return 404 if poem doesn't exist
  if (!poem) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black py-12 px-4">
      <article className="max-w-3xl mx-auto bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-8">
        <header className="mb-8 border-b border-zinc-200 dark:border-zinc-700 pb-6">
          <h1 className="text-4xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">
            {poem.title}
          </h1>
          {poem.author && (
            <p className="text-xl text-zinc-600 dark:text-zinc-400">
              by {poem.author}
            </p>
          )}
        </header>

        <div className="prose prose-zinc dark:prose-invert max-w-none">
          <MDXRemote
            source={poem.content}
            options={{
              mdxOptions: {
                remarkPlugins: [remarkGfm]
              }
            }}
          />
        </div>
      </article>
    </div>
  );
}

// Generate static params for known poems (optional)
export async function generateStaticParams() {
  return Object.keys(poems).map((id) => ({
    id,
  }));
}
