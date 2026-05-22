import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const MODEL_COLORS = {
  "gpt-4.1": "#4de092",
  "claude-sonnet-4-6": "#ff8a3d",
  "gemini-2.5-flash": "#8794ff",
};

export default function ScoreTrendChart({ history }) {
  const chartData = buildChartData(history);
  const modelNames = [
    ...new Set(history.flatMap((run) => run.responses.map((response) => response.model_name))),
  ];

  return (
    <article className="chart-panel">
      <div className="section-heading">
        <h2>Average Score Trend</h2>
        <span>{chartData.length} runs</span>
      </div>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 12, left: -20, bottom: 4 }}>
            <CartesianGrid stroke="#2a2b3b" strokeDasharray="4 4" vertical={false} />
            <XAxis dataKey="run" stroke="#878aa7" />
            <YAxis domain={[0, 10]} stroke="#878aa7" />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            {modelNames.map((modelName, index) => (
              <Line
                dataKey={modelName}
                dot={{ r: 3 }}
                key={modelName}
                name={displayModel(modelName)}
                stroke={MODEL_COLORS[modelName] || fallbackColor(index)}
                strokeWidth={2}
                type="monotone"
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}

function buildChartData(history) {
  return [...history]
    .reverse()
    .map((run, index) => ({
      run: `#${index + 1}`,
      ...Object.fromEntries(
        run.responses.map((response) => [
          response.model_name,
          averageScore(response.scores),
        ]),
      ),
    }));
}

function averageScore(scores) {
  return Number(((scores.relevance + scores.clarity + scores.length) / 3).toFixed(1));
}

function displayModel(modelName) {
  if (modelName.startsWith("gpt")) {
    return "OpenAI";
  }
  if (modelName.startsWith("claude")) {
    return "Claude";
  }
  if (modelName.startsWith("gemini")) {
    return "Gemini";
  }
  return modelName;
}

function fallbackColor(index) {
  return ["#4de092", "#ff8a3d", "#8794ff", "#ef5d93"][index % 4];
}

const tooltipStyle = {
  background: "#11121b",
  border: "1px solid #34364a",
  borderRadius: 8,
  color: "#ececf5",
};
