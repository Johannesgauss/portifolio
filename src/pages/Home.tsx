import { BookOpen, Gamepad2, User, ArrowRight } from 'lucide-react';
import type { TabType } from '../types';
import type { ParsedArticle } from '../articlesLoader';

interface HomeProps {
  onNavigate: (tab: TabType) => void;
  featuredArticle?: ParsedArticle;
  onSelectArticle: (article: ParsedArticle) => void;
}

export function Home({ onNavigate, featuredArticle, onSelectArticle }: HomeProps) {
  return (
    <div className="space-y-12">
      {/* Hero Welcome */}
      <section className="relative overflow-hidden rounded-2xl border border-zinc-800/80 bg-gradient-to-b from-zinc-900/60 to-zinc-950 p-6 sm:p-10">
      {/*<div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-xs mb-6">
          <Terminal className="w-3.5 h-3.5" />
          <span>portfolio.init()</span>
        </div>*/}

        <h1 className="text-3xl sm:text-5xl font-bold tracking-tight text-zinc-100 max-w-3xl leading-tight">
          Computer Science student, backend engineer & systems enthusiast.
        </h1>

        <p className="mt-4 text-base sm:text-lg text-zinc-400 max-w-2xl leading-relaxed">
          Currently in the <strong className="text-zinc-200">4th semester of Computer Science at UFBA</strong>,
          building scalable services as a <strong className="text-zinc-200">Backend Developer at TITAN</strong>,
          and daily-driving a custom <strong className="text-emerald-400 font-mono">Gentoo Linux</strong> system.
        </p>

        {/* Section Cards Overview */}
        <div className="mt-8 pt-8 border-t border-zinc-800/60 grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Articles Hub Card */}
          <div
            onClick={() => onNavigate('articles')}
            className="group cursor-pointer rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 hover:border-zinc-700 hover:bg-zinc-900/80 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center mb-4 border border-blue-500/20 group-hover:scale-105 transition-transform">
                <BookOpen className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-semibold text-zinc-100 group-hover:text-blue-400 transition-colors flex items-center gap-1.5">
                Articles
                <ArrowRight className="w-4 h-4 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
              </h2>
              <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                Texts and technical writeups about low-level programming. 
              </p> {/*, Linux, and backend architectures. Think of it as my personal Medium.*/}
            </div>
            <span className="mt-4 inline-flex items-center text-xs font-mono text-blue-400/90 font-medium">
              Read articles &rarr;
            </span>
          </div>

          {/* Games Hub Card */}
          <div
            onClick={() => onNavigate('games')}
            className="group cursor-pointer rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 hover:border-zinc-700 hover:bg-zinc-900/80 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center mb-4 border border-purple-500/20 group-hover:scale-105 transition-transform">
                <Gamepad2 className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-semibold text-zinc-100 group-hover:text-purple-400 transition-colors flex items-center gap-1.5">
                Games
                <ArrowRight className="w-4 h-4 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
              </h2>
              <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                Yes, GAMES! Because why not? I have even games written in <strong className="text-zinc-200">C & SDL2</strong>! Have fun!
              </p> {/* targeted for WebAssembly via Emscripten for browser play. */}
            </div>
            <span className="mt-4 inline-flex items-center text-xs font-mono text-purple-400/90 font-medium">
              View games &rarr;
            </span>
          </div>

          {/* Info Hub Card */}
          <div
            onClick={() => onNavigate('info')}
            className="group cursor-pointer rounded-xl border border-zinc-800 bg-zinc-900/40 p-5 hover:border-zinc-700 hover:bg-zinc-900/80 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4 border border-emerald-500/20 group-hover:scale-105 transition-transform">
                <User className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-semibold text-zinc-100 group-hover:text-emerald-400 transition-colors flex items-center gap-1.5">
                Info
                <ArrowRight className="w-4 h-4 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
              </h2>
              <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                About me: UFBA Computer Science (4th sem), backend developer at TITAN (empresa júnior), and Gentoo Linux user (I'm a Linux lover).
              </p>
            </div>
            <span className="mt-4 inline-flex items-center text-xs font-mono text-emerald-400/90 font-medium">
              Learn more &rarr;
            </span>
          </div>
        </div>
      </section>

      {/* Highlights & Teasers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Latest Article Teaser */}
        {featuredArticle && (
          <div className="border border-zinc-800 rounded-xl p-6 bg-zinc-900/30 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-zinc-500 mb-3">
                <span className="flex items-center gap-1 text-emerald-400">
                  <BookOpen className="w-3.5 h-3.5" /> Featured Text
                </span>
                <span>{featuredArticle.readTime}</span>
              </div>
              <h3
                className="text-lg font-semibold text-zinc-100 hover:text-emerald-400 cursor-pointer transition-colors"
                onClick={() => {
                  onSelectArticle(featuredArticle);
                  onNavigate('articles');
                }}
              >
                {featuredArticle.title}
              </h3>
              <p className="mt-2 text-sm text-zinc-400 line-clamp-3">{featuredArticle.excerpt}</p>
            </div>
            <div className="mt-4 pt-4 border-t border-zinc-800 flex items-center justify-between">
              <div className="flex gap-2">
                {featuredArticle.tags.slice(0, 2).map((t) => (
                  <span key={t} className="px-2 py-0.5 rounded text-xs font-mono bg-zinc-800 text-zinc-400">
                    {t}
                  </span>
                ))}
              </div>
              <button
                onClick={() => {
                  onSelectArticle(featuredArticle);
                  onNavigate('articles');
                }}
                className="text-xs font-medium text-emerald-400 hover:underline flex items-center gap-1 cursor-pointer"
              >
                Read article <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}

        {/* Cetraminos Game Preview Teaser */}
        <div className="border border-zinc-800 rounded-xl p-6 bg-zinc-900/30 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-zinc-500 mb-3">
              <span className="flex items-center gap-1 text-purple-400">
                <Gamepad2 className="w-3.5 h-3.5" /> Featured Game
              </span>
              <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/30 text-[10px]">
                WebAssembly Ready
              </span>
            </div>
            <h3
              className="text-lg font-semibold text-zinc-100 hover:text-purple-400 cursor-pointer transition-colors"
              onClick={() => onNavigate('games')}
            >
              Cetraminos (C & SDL2)
            </h3>
            <p className="mt-2 text-sm text-zinc-400">
              A custom Tetris-style arcade game with custom piece physics, soundtrack, and font rendering, ready to compile to Wasm via Emscripten.
            </p>
          </div>
          <div className="mt-4 pt-4 border-t border-zinc-800 flex items-center justify-between">
            <span className="text-xs font-mono text-zinc-500">C99 • SDL2 • WebAssembly</span>
            <button
              onClick={() => onNavigate('games')}
              className="text-xs font-medium text-purple-400 hover:underline flex items-center gap-1 cursor-pointer"
            >
              Play Cetraminos <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
