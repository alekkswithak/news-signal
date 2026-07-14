import { ArticleSearchResult } from "../types";

interface Props {
  results: ArticleSearchResult[];
  onAnalyze: (article: ArticleSearchResult) => void;
  analyzingUrl: string | null;
}

function formatDate(iso: string | null): string {
  if (!iso) return "undated";
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function WireList({ results, onAnalyze, analyzingUrl }: Props) {
  if (results.length === 0) {
    return <p className="empty-state">Search a topic to pull recent wire copy.</p>;
  }

  return (
    <div className="wire-list">
      {results.map((article) => (
        <div className="wire-item" key={article.url}>
          <h3>{article.title}</h3>
          <div className="meta">
            {article.source ?? "unknown source"} · {formatDate(article.published_at)}
          </div>
          <div className="wire-item-footer">
            {article.already_analyzed ? (
              <span className="badge-cached">Already analyzed</span>
            ) : (
              <span />
            )}
            <button
              className="analyze-btn"
              disabled={analyzingUrl === article.url}
              onClick={() => onAnalyze(article)}
            >
              {analyzingUrl === article.url
                ? "Analyzing…"
                : article.already_analyzed
                ? "View analysis"
                : "Analyze"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
