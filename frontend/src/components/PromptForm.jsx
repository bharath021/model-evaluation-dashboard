import { Play } from "lucide-react";

export default function PromptForm({
  onPresetSelect,
  onPromptChange,
  onRun,
  presets,
  prompt,
  running,
}) {
  return (
    <section className="prompt-panel" aria-label="Evaluation prompt">
      <label htmlFor="eval-prompt">Eval Prompt</label>
      <textarea
        id="eval-prompt"
        onChange={(event) => onPromptChange(event.target.value)}
        value={prompt}
      />

      <div className="prompt-actions">
        <button
          className="run-button"
          disabled={!prompt.trim() || running}
          onClick={onRun}
          type="button"
        >
          <Play />
          {running ? "Running..." : "Run Evaluation"}
        </button>

        <span className="preset-label">Presets:</span>
        <div className="preset-buttons">
          {presets.map((preset) => (
            <button
              key={preset.label}
              onClick={() => onPresetSelect(preset.prompt)}
              type="button"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
