import { useEffect, useState } from "react";
import { executionConfig } from "../data/executionConfig";

export default function useExecution() {
  const [steps, setSteps] = useState(
    executionConfig.steps.map((step) => ({
      ...step,
      status: "pending",
    }))
  );

  const [running, setRunning] = useState(false);

  const [currentTarget, setCurrentTarget] = useState(null);

  function start() {
    if (running) return;

    setSteps(
      executionConfig.steps.map((step) => ({
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

    executionConfig.steps.forEach((step, index) => {
      const timer = setTimeout(() => {
        setSteps((previousSteps) =>
          previousSteps.map((currentStep, currentIndex) => {
            if (currentIndex < index) {
              return {
                ...currentStep,
                status: "complete",
              };
            }

            if (currentIndex === index) {
              return {
                ...currentStep,
                status: "active",
              };
            }

            return {
              ...currentStep,
              status: "pending",
            };
          })
        );

        setCurrentTarget(step.target);
      }, index * 1200);

      timers.push(timer);
    });

    const finishTimer = setTimeout(() => {
      setSteps((previousSteps) =>
        previousSteps.map((step) => ({
          ...step,
          status: "complete",
        }))
      );

      setCurrentTarget(null);
      setRunning(false);
    }, executionConfig.steps.length * 1200);

    timers.push(finishTimer);

    return () => {
      timers.forEach(clearTimeout);
    };
  }, [running]);

  return {
    steps,
    running,
    currentTarget,
    start,
  };
}