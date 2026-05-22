export default function ScoreBadge({ label, value }) {
  let level = "low";
  if (value >= 8) {
    level = "high";
  } else if (value >= 5) {
    level = "medium";
  }

  return (
    <span className={`score-badge ${level}`}>
      {label} {value}
    </span>
  );
}
