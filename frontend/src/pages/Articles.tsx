import { useState } from 'react';
import { BookOpen, Calendar, Clock, ChevronLeft, Search } from 'lucide-react';
import type { ParsedArticle } from '../articlesLoader';

interface ArticlesProps {
  articles: ParsedArticle[];
  selectedArticle: ParsedArticle | null;
  onSelectArticle: (article: ParsedArticle | null) => void;
}

export function Articles({ articles, selectedArticle, onSelectArticle }: ArticlesProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string>('All');

  const allTags = ['All', ...Array.from(new Set(articles.flatMap((a) => a.tags)))];

  const filteredArticles = articles.filter((article) => {
    const matchesTag = selectedTag === 'All' || article.tags.includes(selectedTag);
    const matchesSearch =
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTag && matchesSearch;
  });

  return (
    <div>
      {selectedArticle ? (
        /* Full Article Reader Mode (Medium Style) */
        <article className="max-w-3xl mx-auto space-y-8 animate-in fade-in duration-200">
          <button
            onClick={() => onSelectArticle(null)}
            className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-100 transition-colors cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" /> Back to all articles
          </button>

          <header className="space-y-4">
            <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-zinc-400">
              <span className="text-emerald-400">{selectedArticle.date}</span>
              <span>•</span>
              <span>{selectedArticle.readTime}</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-zinc-100 leading-snug">
              {selectedArticle.title}
            </h1>
            <p className="text-lg text-zinc-400 italic">{selectedArticle.excerpt}</p>
            <div className="flex flex-wrap gap-2 pt-2">
              {selectedArticle.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2.5 py-1 rounded-full text-xs font-mono bg-zinc-800/80 text-zinc-300 border border-zinc-700/60"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </header>

          <hr className="border-zinc-800" />

          {/* Rendered HTML with cleanly separated .article-markdown stylesheet */}
          <div
            className="article-markdown space-y-4"
            dangerouslySetInnerHTML={{ __html: selectedArticle.htmlContent }}
          />
        </article>
      ) : (
        /* Articles Feed */
        <div className="space-y-8">
          {/* Header */}
          <div className="border-b border-zinc-800 pb-6">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 mb-2">
              <BookOpen className="w-4 h-4" />
              <span>PUBLICATION / ESSAYS</span>
            </div>
            <h1 className="text-3xl font-bold text-zinc-100">Articles</h1>
            <p className="mt-2 text-zinc-400 text-sm sm:text-base">
              Articles on software development, Linux internals, C programming and systems design.
            </p>
              {/*Medium-style texts on software development, Linux internals, C programming, and systems design.
              Edit or add new posts in <code className="text-emerald-400 font-mono text-xs">src/content/articles/*.md</code>. */}
            {/* Filter and Search */}
            <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
              {/* Tags */}
              <div className="flex flex-wrap gap-1.5">
                {allTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => setSelectedTag(tag)}
                    className={`px-3 py-1 rounded-full text-xs font-mono transition-colors cursor-pointer ${
                      selectedTag === tag
                        ? 'bg-zinc-100 text-zinc-950 font-semibold'
                        : 'bg-zinc-900 text-zinc-400 border border-zinc-800 hover:border-zinc-700'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>

              {/* Search Bar */}
              <div className="relative w-full sm:w-64">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                <input
                  type="text"
                  placeholder="Search texts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-zinc-900/80 border border-zinc-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 font-mono"
                />
              </div>
            </div>
          </div>

          {/* Articles List */}
          <div className="divide-y divide-zinc-800/80">
            {filteredArticles.map((article) => (
              <article
                key={article.id}
                onClick={() => {
                  onSelectArticle(article);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                className="py-8 group cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-2 text-xs font-mono text-zinc-500 mb-2">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{article.date}</span>
                  <span>•</span>
                  <Clock className="w-3.5 h-3.5" />
                  <span>{article.readTime}</span>
                </div>

                <h2 className="text-xl sm:text-2xl font-bold text-zinc-100 group-hover:text-emerald-400 transition-colors">
                  {article.title}
                </h2>

                <p className="mt-2 text-zinc-400 text-sm sm:text-base leading-relaxed line-clamp-2">
                  {article.excerpt}
                </p>

                <div className="mt-4 flex items-center justify-between">
                  <div className="flex flex-wrap gap-2">
                    {article.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 rounded text-xs font-mono bg-zinc-900 text-zinc-400 border border-zinc-800"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <span className="text-xs font-mono text-emerald-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1 font-medium">
                    Read full text &rarr;
                  </span>
                </div>
              </article>
            ))}

            {filteredArticles.length === 0 && (
              <div className="py-12 text-center text-zinc-500 font-mono text-sm">
                No articles match your search query.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
