import { Sentiment } from "../types";

interface Props {
  sentiment: Sentiment;
  score: number;
}

const COLORS: Record<Sentiment, string> = {
  positive: "var(--teal)",
  neutral: "var(--amber)",
  negative: "var(--rust)",
};

// Amplitude scales with |score| so the line itself communicates intensity,
// not just the color - a flat line reads as "neutral" without needing a legend.
function buildPath(score: number): string {
  const amplitude = Math.max(2, Math.min(10, Math.abs(score) * 10));
  const dir = score >= 0 ? -1 : 1;
  return `M0,12 C8,${12 + dir * amplitude} 16,${12 - dir * amplitude} 24,12 S40,${
    12 + dir * amplitude
  } 48,12 S64,${12 - dir * amplitude} 72,12`;
}

export function SentimentPulse({ sentiment, score }: Props) {
  const color = COLORS[sentiment];
  return (
    <div className="pulse-row">
      <svg width="72" height="24" viewBox="0 0 72 24" aria-hidden="true">
        <path
          d={buildPath(score)}
          fill="none"
          stroke={color}
          strokeWidth="1.8"
          strokeLinecap="round"
        >
          <animate
            attributeName="stroke-opacity"
            values="0.55;1;0.55"
            dur="2.4s"
            repeatCount="indefinite"
          />
        </path>
      </svg>
      <span className="pulse-label" style={{ color }}>
        {sentiment} · {score >= 0 ? "+" : ""}
        {score.toFixed(2)}
      </span>
    </div>
  );
}
