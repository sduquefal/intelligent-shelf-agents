import "./index.css";

import Header from "./components/Header/Header";
import PlatformCanvas from "./components/PlatformCanvas/PlatformCanvas";
import ExecutionPanel from "./components/ExecutionPanel/ExecutionPanel";
import useExecution from "./hooks/useExecution";

export default function App() {
  const {
    scenario,
    scenarioIndex,
    scenarios,
    steps,
    running,
    currentTarget,
    selectScenario,
    start,
  } = useExecution();

  return (
    <>
      <Header />

      <main className="layout">
        <PlatformCanvas
          currentTarget={currentTarget}
        />

        <ExecutionPanel
          scenario={scenario}
          scenarioIndex={scenarioIndex}
          scenarios={scenarios}
          steps={steps}
          running={running}
          onSelectScenario={selectScenario}
          onStart={start}
        />
      </main>
    </>
  );
}