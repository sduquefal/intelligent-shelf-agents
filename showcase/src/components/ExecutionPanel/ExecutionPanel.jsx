import "./ExecutionPanel.css";

import ResultCard from "../ResultCard/ResultCard";

export default function ExecutionPanel({
  scenario,
  scenarioIndex,
  scenarios,
  steps,
  running,
  onSelectScenario,
  onStart,
}) {
  const { question, result } = scenario;

  const finished =
    !running &&
    steps.length > 0 &&
    steps.every((step) => step.status === "complete");

  return (
    <aside className="execution-panel">
      <div className="execution-heading">
        <div>
          <span className="eyebrow">
            LIVE EXECUTION
          </span>

          <h2>
            How the platform responds
          </h2>
        </div>

        <span className="execution-status">
          <span
            className={`status-dot ${
              running ? "running" : ""
            }`}
          />

          {running ? "Running" : "Ready"}
        </span>
      </div>

      <div className="question-block">
        <span className="question-label">
          Scenario
        </span>

        <select
          className="scenario-select"
          value={scenarioIndex}
          onChange={(event) =>
            onSelectScenario(Number(event.target.value))
          }
          disabled={running}
        >
          {scenarios.map((item, index) => (
            <option
              key={item.id}
              value={index}
            >
              {item.question}
            </option>
          ))}
        </select>

        <span className="question-label question-label-spaced">
          Question
        </span>

        <div className="question-box">
          <span>
            {question}
          </span>

          <button
            className="run-button"
            onClick={onStart}
            disabled={running}
          >
            {running ? "Running..." : "Run"}
          </button>
        </div>
      </div>

      <div className="timeline">
        {steps.map((step) => (
          <div
            key={step.id}
            className={`timeline-item ${step.status}`}
          >
            <div className="timeline-marker">
              {step.status === "complete" && "✓"}

              {step.status === "active" && (
                <span className="pulse" />
              )}
            </div>

            <div>
              <strong>
                {step.title}
              </strong>

              <span>
                {step.detail}
              </span>
            </div>
          </div>
        ))}
      </div>

      {finished && (
        <ResultCard
          result={result}
          resultType={scenario.resultType}
        />
      )}
    </aside>
  );
}