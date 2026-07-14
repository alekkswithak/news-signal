export type Sentiment = "positive" | "neutral" | "negative";

export interface ArticleSearchResult {
  url: string;
  title: string;
  description: string | null;
  source: string | null;
  image: string | null;
  published_at: string | null;
  already_analyzed: boolean;
}

export interface AnalyzedArticle {
  url: string;
  title: string;
  description: string | null;
  source: string | null;
  published_at: string | null;
  summary: string;
  sentiment: Sentiment;
  sentiment_score: number;
  analyzed_at: string;
  from_cache: boolean;
}
