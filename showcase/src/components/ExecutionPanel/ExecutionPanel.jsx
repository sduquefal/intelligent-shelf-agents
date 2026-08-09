import "./ExecutionPanel.css";

import ResultCard from "../ResultCard/ResultCard";
import { executionConfig } from "../../data/executionConfig";

export default function ExecutionPanel({
  steps,
  running,
  onStart,
}) {
  const { question, result } = executionConfig;

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

      {!running &&
        steps.every(
          (step) => step.status === "complete"
        ) && (
          <>
            <ResultCard result={result} />
          </>
        )}
    </aside>
  );
}