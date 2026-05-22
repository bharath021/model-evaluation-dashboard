import { useCallback, useEffect, useState } from "react";

import { fetchHistory, fetchModels, runEvaluation } from "../services/api.js";

export function useEvaluations() {
  const [models, setModels] = useState([]);
  const [history, setHistory] = useState([]);
  const [activeRun, setActiveRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [modelsPayload, historyPayload] = await Promise.all([
        fetchModels(),
        fetchHistory(),
      ]);
      setModels(modelsPayload.models);
      setHistory(historyPayload.runs);
      setActiveRun((current) => current || historyPayload.runs[0] || null);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const evaluate = useCallback(async (prompt) => {
    setRunning(true);
    setError("");

    try {
      const run = await runEvaluation(prompt);
      setActiveRun(run);
      setHistory((currentHistory) => [run, ...currentHistory]);
      return run;
    } catch (evaluationError) {
      setError(evaluationError.message);
      return null;
    } finally {
      setRunning(false);
    }
  }, []);

  return {
    activeRun,
    error,
    evaluate,
    history,
    loading,
    models,
    running,
    setActiveRun,
  };
}
