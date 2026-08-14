import { useEffect, useState } from "react";
import { executionScenarios } from "../data/executionConfig";

export default function useExecution() {
  const [scenarioIndex, setScenarioIndex] = useState(0);
  const scenario = executionScenarios[scenarioIndex];

  const [steps, setSteps] = useState(
    scenario.steps.map((step) => ({
      ...step,
      status: "pending",
    }))
  );

  const [running, setRunning] = useState(false);
  const [currentTarget, setCurrentTarget] = useState(null);

  function selectScenario(index) {
    if (running) return;

    setScenarioIndex(index);

    setSteps(
      executionScenarios[index].steps.map((step) => ({
        ...step,
        status: "pending",
      }))
    );

    setCurrentTarget(null);
  }

  function start() {
    if (running) return;

    setSteps(
      scenario.steps.map((step) => ({
        ...step,
        status: "pending",
      }))
    );

    setCurrentTarget(null);
    setRunning(true);
  }

  useEffect(() => {
    if (!running) return;

    const timers = [];

    scenario.steps.forEach((step, index) => {
      timers.push(
        setTimeout(() => {
          setSteps((previousSteps) =>
            previousSteps.map((currentStep, currentIndex) => ({
              ...currentStep,
              status:
                currentIndex < index
                  ? "complete"
                  : currentIndex === index
                  ? "active"
                  : "pending",
            }))
          );

          setCurrentTarget(step.target);
        }, index * 1200)
      );
    });

    timers.push(
      setTimeout(() => {
        setSteps((previousSteps) =>
          previousSteps.map((step) => ({
            ...step,
            status: "complete",
          }))
        );

        setCurrentTarget(null);
        setRunning(false);
      }, scenario.steps.length * 1200)
    );

    return () => timers.forEach(clearTimeout);
  }, [running]);

  return {
    scenario,
    scenarioIndex,
    scenarios: executionScenarios,
    steps,
    running,
    currentTarget,
    selectScenario,
    start,
  };
}