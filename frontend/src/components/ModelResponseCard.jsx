import ScoreBadge from "./ScoreBadge.jsx";

const MODEL_DETAILS = {
  openai: {
    className: "openai",
    code: "G4",
    title: "GPT-4o",
  },
  anthropic: {
    className: "anthropic",
    code: "CL",
    title: "Claude Sonnet",
  },
  google: {
    className: "google",
    code: "GM",
    title: "Gemini Pro",
  },
};

export default function ModelResponseCard({ loading, model }) {
  const details = MODEL_DETAILS[model.provider] || {
    className: "default",
    code: model.display_name.slice(0, 2).toUpperCase(),
    title: model.display_name,
  };
  const response = model.response;

  return (
    <article className="response-card">
      <header>
        <span className={`model-code ${details.className}`}>{details.code}</span>
        <div>
          <h3>{details.title}</h3>
          <p>
            {model.provider} . {model.model_name}
          </p>
        </div>
      </header>

      <div className={response ? "response-copy ready" : "response-copy"}>
        {response?.response_text || (loading ? "Contacting models..." : "Waiting for prompt...")}
      </div>

      {response ? (
        <footer>
          <div className="score-row">
            <ScoreBadge label="Rel" value={response.scores.relevance} />
            <ScoreBadge label="Clr" value={response.scores.clarity} />
            <ScoreBadge label="Len" value={response.scores.length} />
          </div>
          <span className="latency">{response.response_time_ms} ms</span>
        </footer>
      ) : null}
    </article>
  );
}
