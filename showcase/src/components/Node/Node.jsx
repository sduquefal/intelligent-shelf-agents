import "./Node.css";

export default function Node({
  title,
  subtitle,
  color,
  active,
}) {
  return (
    <div className={`node ${active ? "active" : ""}`}>
      <div
        className="node-icon"
        style={{ background: color }}
      />

      <h3>{title}</h3>

      <span>{subtitle}</span>
    </div>
  );
}