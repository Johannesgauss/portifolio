import { useState, useEffect } from 'react';
import type { TabType } from './types';
import { loadArticles, type ParsedArticle } from './articlesLoader';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { Home } from './pages/Home';
import { Articles } from './pages/Articles';
import { Games } from './pages/Games';
import { Info } from './pages/Info';

export function App() {
  const articles = loadArticles();
  const [currentTab, setCurrentTab] = useState<TabType>('home');
  const [selectedArticle, setSelectedArticle] = useState<ParsedArticle | null>(null);

  // Sync tab with URL hash for clean navigation
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '') as TabType;
      if (['home', 'articles', 'games', 'info'].includes(hash)) {
        setCurrentTab(hash);
        setSelectedArticle(null);
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const navigateToTab = (tab: TabType) => {
    setCurrentTab(tab);
    window.location.hash = tab;
    setSelectedArticle(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectArticle = (article: ParsedArticle | null) => {
    setSelectedArticle(article);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-200">
      {/* Navigation Header */}
      <Navbar currentTab={currentTab} onSelectTab={navigateToTab} />

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {currentTab === 'home' && (
          <Home
            onNavigate={navigateToTab}
            featuredArticle={articles[0]}
            onSelectArticle={handleSelectArticle}
          />
        )}

        {currentTab === 'articles' && (
          <Articles
            articles={articles}
            selectedArticle={selectedArticle}
            onSelectArticle={handleSelectArticle}
          />
        )}

        {currentTab === 'games' && <Games />}

        {currentTab === 'info' && <Info />}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
