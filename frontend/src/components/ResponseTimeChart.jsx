import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function ResponseTimeChart({ run }) {
  const chartData = run.responses.map((response) => ({
    model: displayModel(response.model_name),
    time: response.response_time_ms,
  }));

  return (
    <article className="chart-panel">
      <div className="section-heading">
        <h2>Response Time</h2>
        <span>Latest run</span>
      </div>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 12, left: -12, bottom: 4 }}>
            <CartesianGrid stroke="#2a2b3b" strokeDasharray="4 4" vertical={false} />
            <XAxis dataKey="model" stroke="#878aa7" />
            <YAxis stroke="#878aa7" unit="ms" />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="time" fill="#7d77ff" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
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

const tooltipStyle = {
  background: "#11121b",
  border: "1px solid #34364a",
  borderRadius: 8,
  color: "#ececf5",
};
