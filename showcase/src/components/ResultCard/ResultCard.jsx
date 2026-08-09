import "./ResultCard.css";

export default function ResultCard({ result }) {
  return (
    <section className="result-card">
      <div className="result-top">
        <div>
          <span className="result-label">
            RESULT
          </span>

          <h3>{result.store}</h3>

          <p>Store {result.storeCode}</p>
        </div>

        <span className="live-badge">
          LIVE DATA
        </span>
      </div>

      <div className="primary-result">
        <span>SNSG</span>

        <strong>
          {result.snsg.toFixed(1)}%
        </strong>
      </div>

      <div className="secondary-results">
        <div>
          <span>Bodega</span>

          <strong className="bodega">
            {result.bodega.toFixed(2)}%
          </strong>
        </div>

        <div>
          <span>Quiebre</span>

          <strong className="quiebre">
            {result.quiebre.toFixed(2)}%
          </strong>
        </div>
      </div>

      <div className="result-volume">
        {result.total.toLocaleString()} products analyzed
      </div>
    </section>
  );
}