import { useEffect, useState } from "react";
import { SearchBar } from "./components/SearchBar";
import { WireList } from "./components/WireList";
import { DispatchFeed } from "./components/DispatchFeed";
import { api } from "./api/client";
import { ArticleSearchResult, AnalyzedArticle } from "./types";

export default function App() {
  const [results, setResults] = useState<ArticleSearchResult[]>([]);
  const [dispatches, setDispatches] = useState<AnalyzedArticle[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [analyzingUrl, setAnalyzingUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .history()
      .then(setDispatches)
      .catch((e) => setError(e.message));
  }, []);

  async function handleSearch(query: string) {
    setIsSearching(true);
    setError(null);
    try {
      const found = await api.search(query);
      setResults(found);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setIsSearching(false);
    }
  }

  async function handleAnalyze(article: ArticleSearchResult) {
    setAnalyzingUrl(article.url);
    setError(null);
    try {
      const analyzed = await api.analyze({
        url: article.url,
        title: article.title,
        description: article.description,
        source: article.source,
        published_at: article.published_at,
      });

      setResults((prev) =>
        prev.map((r) => (r.url === article.url ? { ...r, already_analyzed: true } : r))
      );

      setDispatches((prev) => {
        const withoutDuplicate = prev.filter((d) => d.url !== analyzed.url);
        return [analyzed, ...withoutDuplicate];
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalyzingUrl(null);
    }
  }

  return (
    <div className="app">
      <header className="masthead">
        <h1>News Signal</h1>
        <span className="dateline">Wire desk · AI sentiment &amp; summary analysis</span>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="layout">
        <section>
          <div className="panel-label">Incoming wire</div>
          <SearchBar onSearch={handleSearch} isSearching={isSearching} />
          <WireList results={results} onAnalyze={handleAnalyze} analyzingUrl={analyzingUrl} />
        </section>

        <section>
          <div className="panel-label">Filed dispatches</div>
          <DispatchFeed dispatches={dispatches} />
        </section>
      </div>
    </div>
  );
}
