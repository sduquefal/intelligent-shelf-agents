import "./PlatformCanvas.css";
import { platformConfig } from "../../data/platformConfig";
import Node from "../Node/Node";

export default function PlatformCanvas({
  currentTarget,
}) {
  const {
    agent,
    services,
    intelligence,
    foundation,
  } = platformConfig;

  return (
    <section className="canvas">
      <div className="canvas-title">
        AI REASONING CANVAS
      </div>

      <Node
        title={agent.name}

        subtitle={agent.subtitle}

        color="#78BE20"

        active={

        currentTarget==="shelf-analyst"

        }

        />

      <div className="services">
        {services.map(service=>(
        <Node
        key={service.id}
        title={service.name}
        subtitle={service.description}
        color={
        service.type==="store"
        ?"#78BE20"
        :
        service.type==="analytics"
        ?"#3478D4"
        :"#E5484D"
        }

        active={ currentTarget===service.id}

        />

        ))}

      </div>

     <section
        className={`intelligence-layer ${
            currentTarget === "shared-intelligence"
            ? "active"
            : ""
        }`}
        >
        <h3>{intelligence.name}</h3>

        <div className="layer-items">
            {intelligence.items.map((item) => (
            <span key={item}>{item}</span>
            ))}
        </div>
        </section>

      <section className="foundation-layer">
        <h3>{foundation.name}</h3>

        <div className="foundation-items">
          {foundation.items.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </section>
    </section>
  );
}