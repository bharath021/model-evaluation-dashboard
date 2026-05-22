import { Activity, Play, Zap } from "lucide-react";
import { useMemo, useState } from "react";

import ModelResponseCard from "../components/ModelResponseCard.jsx";
import PromptForm from "../components/PromptForm.jsx";
import ResponseTimeChart from "../components/ResponseTimeChart.jsx";
import ScoreTrendChart from "../components/ScoreTrendChart.jsx";
import { useEvaluations } from "../hooks/useEvaluations.js";

const PRESETS = [
  {
    label: "Recursion",
    prompt: "Explain recursion with a concise Python example.",
  },
  {
    label: "Microservices",
    prompt: "Compare monoliths and microservices for a small engineering team.",
  },
  {
    label: "Palindrome",
    prompt: "Write a Python function to detect palindromes.",
  },
];

const DEFAULT_PROMPT = PRESETS[2].prompt;

export default function Dashboard() {
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const {
    activeRun,
    error,
    evaluate,
    history,
    loading,
    models,
    running,
    setActiveRun,
  } = useEvaluations();

  const visibleModels = useMemo(() => {
    return models.map((model) => ({
      ...model,
      response: findResponse(model, activeRun?.responses || []),
    }));
  }, [activeRun, models]);

  const handleRun = async () => {
    if (!prompt.trim()) {
      return;
    }

    await evaluate(prompt.trim());
  };

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div className="brand-mark" aria-hidden="true">
          <Zap />
        </div>
        <div className="brand-copy">
          <h1>Model Eval Dashboard</h1>
          <p>MLOps . LLM Benchmarking . Real-time</p>
        </div>
        <span className="live-dot" aria-label="Backend connected" />
      </header>

      <PromptForm
        prompt={prompt}
        presets={PRESETS}
        running={running}
        onPromptChange={setPrompt}
        onPresetSelect={setPrompt}
        onRun={handleRun}
      />

      {error ? <p className="api-error">{error}</p> : null}

      <section className="responses-section" aria-labelledby="responses-title">
        <div className="section-heading">
          <h2 id="responses-title">Model Responses</h2>
          <span>{models.length || 3} models</span>
        </div>

        <div className="response-grid">
          {(visibleModels.length ? visibleModels : fallbackModels()).map((model) => (
            <ModelResponseCard
              key={model.model_name}
              model={model}
              loading={loading || running}
            />
          ))}
        </div>
      </section>

      {history.length ? (
        <section className="charts-grid" aria-label="Evaluation charts">
          <ScoreTrendChart history={history} />
          <ResponseTimeChart run={activeRun || history[0]} />
        </section>
      ) : null}

      <section className="history-panel" aria-labelledby="history-title">
        <div className="section-heading">
          <h2 id="history-title">Eval History</h2>
          <span>{history.length} runs</span>
        </div>

        {history.length ? (
          <div className="history-list">
            {history.map((run) => (
              <button
                className={run.id === activeRun?.id ? "history-run active" : "history-run"}
                key={run.id}
                onClick={() => setActiveRun(run)}
                type="button"
              >
                <strong>{run.prompt}</strong>
                <span>
                  <Activity />
                  {formatCreatedAt(run.created_at)}
                </span>
              </button>
            ))}
          </div>
        ) : (
          <p className="empty-history">
            No evaluations yet. Run your first eval above <Play />
          </p>
        )}
      </section>
    </main>
  );
}

function fallbackModels() {
  return [
    {
      provider: "openai",
      model_name: "gpt-4.1",
      display_name: "OpenAI",
      configured: true,
      mode: "mock",
    },
    {
      provider: "anthropic",
      model_name: "claude-sonnet-4-6",
      display_name: "Claude",
      configured: true,
      mode: "mock",
    },
    {
      provider: "google",
      model_name: "gemini-2.5-flash",
      display_name: "Gemini",
      configured: true,
      mode: "mock",
    },
  ];
}

function findResponse(model, responses) {
  return (
    responses.find((response) => response.model_name === model.model_name) ||
    responses.find((response) => providerForModel(response.model_name) === model.provider)
  );
}

function providerForModel(modelName) {
  if (modelName.startsWith("gpt")) {
    return "openai";
  }
  if (modelName.startsWith("claude")) {
    return "anthropic";
  }
  if (modelName.startsWith("gemini")) {
    return "google";
  }
  return "";
}

function formatCreatedAt(createdAt) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(createdAt));
}
