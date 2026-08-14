import "./ResultCard.css";

function formatChange(value) {
  if (typeof value !== "number") return "—";

  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)} pp`;
}

function InsightBlocks({ result }) {
  return (
    <>
      {result.insight && (
        <div className="result-insight">
          <span>INSIGHT</span>
          <p>{result.insight}</p>
        </div>
      )}

      {result.action && (
        <div className="result-action">
          <span>RECOMMENDED ACTION</span>
          <p>{result.action}</p>
        </div>
      )}
    </>
  );
}

function StoreResult({ result }) {
  return (
    <>
      <div className="result-top">
        <div>
          <span className="result-label">RESULT</span>
          <h3>{result.store}</h3>

          <p>
            Store {result.storeCode}
            {result.date ? ` · ${result.date}` : ""}
          </p>
        </div>

        <span className="live-badge">
          DEMO DATA
        </span>
      </div>

      <div className="primary-result">
        <span>SNSG</span>

        <strong>
          {result.snsg?.toFixed(2) ?? "—"}%
        </strong>

        <small>
          {formatChange(result.change?.snsg)} vs previous day
        </small>
      </div>

      <div className="secondary-results">
        <div>
          <span>Bodega</span>

          <strong className="bodega">
            {result.bodega?.toFixed(2) ?? "—"}%
          </strong>

          <small>
            {formatChange(result.change?.bodega)}
          </small>
        </div>

        <div>
          <span>Quiebre</span>

          <strong className="quiebre">
            {result.quiebre?.toFixed(2) ?? "—"}%
          </strong>

          <small>
            {formatChange(result.change?.quiebre)}
          </small>
        </div>
      </div>

      {typeof result.total === "number" && (
        <div className="result-volume">
          {result.total.toLocaleString()} products analyzed
        </div>
      )}

      <InsightBlocks result={result} />
    </>
  );
}

function TrendResult({ result }) {
  return (
    <>
      <div className="result-top">
        <div>
          <span className="result-label">
            7-DAY TREND
          </span>

          <h3>{result.store}</h3>

          <p>
            Store {result.storeCode} · Last {result.days} days
          </p>
        </div>

        <span className="live-badge">
          DEMO DATA
        </span>
      </div>

      <div className="primary-result">
        <span>SNSG CHANGE</span>

        <strong>
          {formatChange(result.snsgChange)}
        </strong>
      </div>

      <div className="secondary-results">
        <div>
          <span>Bodega change</span>

          <strong className="bodega">
            {formatChange(result.bodegaChange)}
          </strong>
        </div>

        <div>
          <span>Quiebre change</span>

          <strong className="quiebre">
            {formatChange(result.quiebreChange)}
          </strong>
        </div>
      </div>

      <InsightBlocks result={result} />
    </>
  );
}

function RankingResult({ result }) {
  return (
    <>
      <div className="result-top">
        <div>
          <span className="result-label">
            PRIORITY STORES
          </span>

          <h3>{result.country}</h3>

          <p>{result.date}</p>
        </div>

        <span className="live-badge">
          DEMO DATA
        </span>
      </div>

      <div className="ranking-list">
        {result.ranking?.map((store, index) => (
          <div
            className="ranking-row"
            key={store.storeCode}
          >
            <span className="ranking-position">
              {index + 1}
            </span>

            <div className="ranking-store">
              <strong>{store.store}</strong>

              <span>
                Store {store.storeCode} ·
                Bodega {store.bodega.toFixed(2)}% ·
                Quiebre {store.quiebre.toFixed(2)}%
              </span>
            </div>

            <strong className="ranking-snsg">
              {store.snsg.toFixed(2)}%
            </strong>
          </div>
        ))}
      </div>

      <InsightBlocks result={result} />
    </>
  );
}

export default function ResultCard({
  result,
  resultType = "store",
}) {
  if (!result) return null;

  return (
    <section className="result-card">
      {resultType === "store" && (
        <StoreResult result={result} />
      )}

      {resultType === "trend" && (
        <TrendResult result={result} />
      )}

      {resultType === "ranking" && (
        <RankingResult result={result} />
      )}
    </section>
  );
}