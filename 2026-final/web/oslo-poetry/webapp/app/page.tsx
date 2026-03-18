
import Link from 'next/link';

const poems = [
  {
    id: 'the-raven',
    title: 'The Raven',
    author: 'Edgar Allan Poe',
    year: '1845',
    description: 'A narrative poem about a talking raven\'s mysterious visit to a distraught lover.'
  },
  {
    id: 'the-bells',
    title: 'The Bells',
    author: 'Edgar Allan Poe',
    year: '1849',
    description: 'A heavily onomatopoetic poem exploring the sounds and emotions of different types of bells.'
  }
];

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 font-sans dark:bg-black">
      <div className="max-w-4xl mx-auto py-16 px-4">
        <header className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 text-zinc-900 dark:text-zinc-100">
            The Oslo Poetry Research Organization
          </h1>
          <p className="text-xl text-zinc-600 dark:text-zinc-400">
            Exploring the depths of literary excellence
          </p>
        </header>

        <section>
          <h2 className="text-3xl font-semibold mb-8 text-zinc-900 dark:text-zinc-100">
            Well Studied Poems
          </h2>

          <div className="grid gap-6 md:grid-cols-2">
            {poems.map((poem) => (
              <Link
                key={poem.id}
                href={`/poems/${poem.id}`}
                className="block bg-white dark:bg-zinc-900 rounded-lg shadow-md hover:shadow-xl transition-shadow p-6 border border-zinc-200 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-600"
              >
                <h3 className="text-2xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">
                  {poem.title}
                </h3>
                <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">
                  by {poem.author} ({poem.year})
                </p>
                <p className="text-zinc-700 dark:text-zinc-300">
                  {poem.description}
                </p>
              </Link>
            ))}

            <Link
              href="/poems/new"
              className="flex items-center justify-center bg-white dark:bg-zinc-900 rounded-lg shadow-md hover:shadow-xl transition-shadow p-6 border-2 border-dashed border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-500"
            >
              <div className="text-center">
                <div className="text-6xl font-light text-zinc-400 dark:text-zinc-600 mb-2">
                  +
                </div>
                <p className="text-lg text-zinc-600 dark:text-zinc-400">
                  Preview Your Poem
                </p>
              </div>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
