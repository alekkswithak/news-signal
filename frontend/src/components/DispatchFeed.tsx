import { AnalyzedArticle } from "../types";
import { SentimentPulse } from "./SentimentPulse";

interface Props {
  dispatches: AnalyzedArticle[];
}

function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function DispatchFeed({ dispatches }: Props) {
  if (dispatches.length === 0) {
    return (
      <p className="empty-state">
        No dispatches yet. Analyze an article from the wire to file the first one.
      </p>
    );
  }

  return (
    <div className="dispatch-grid">
      {dispatches.map((d) => (
        <article className="dispatch-card" key={d.url}>
          <h3>
            <a href={d.url} target="_blank" rel="noreferrer">
              {d.title}
            </a>
          </h3>
          <div className="meta">
            {d.source ?? "unknown source"} · filed {formatTimestamp(d.analyzed_at)}
            {d.from_cache ? " · served from cache" : ""}
          </div>
          <p className="summary">{d.summary}</p>
          <SentimentPulse sentiment={d.sentiment} score={d.sentiment_score} />
        </article>
      ))}
    </div>
  );
}
