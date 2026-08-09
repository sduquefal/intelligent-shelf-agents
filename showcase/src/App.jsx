import "./index.css";

import Header from "./components/Header/Header";
import PlatformCanvas from "./components/PlatformCanvas/PlatformCanvas";
import ExecutionPanel from "./components/ExecutionPanel/ExecutionPanel";
import useExecution from "./hooks/useExecution";

export default function App() {
  const {
    steps,
    running,
    currentTarget,
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
          steps={steps}
          running={running}
          onStart={start}
        />
      </main>
    </>
  );
}