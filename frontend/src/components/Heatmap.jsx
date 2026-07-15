function fmt(n) {
  return "₹" + Math.round(n).toLocaleString("en-IN");
}

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function Heatmap({ data, onSelectDay }) {
  if (!data) return null;

  return (
    <>
      <div className="heatmap-calendar">
        <div className="heatmap-month-header">{data.month_label}</div>
        <div className="heatmap-weekdays">
          {WEEKDAYS.map((d) => <div key={d} className="heatmap-weekday">{d}</div>)}
        </div>
        <div className="heatmap-days">
          {Array.from({ length: data.first_weekday }).map((_, i) => (
            <div key={`empty-${i}`} className="heat-day empty" />
          ))}
          {data.days.map((d) => (
            <div
              key={d.day}
              className={`heat-day ${d.level}`}
              title={fmt(d.price)}
              onClick={() => onSelectDay?.(d)}
            >
              <span className="day-num">{d.day}</span>
              <span className="day-price">{fmt(d.price)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="cheapest-days">
        {data.cheapest.map((d, i) => (
          <div className="cheapest-item" key={d.day}>
            <div className="ci-rank">#{i + 1}</div>
            <div>
              <div className="ci-date">{data.month_label.split(" ")[0]} {d.day}</div>
              <div className="ci-price">{fmt(d.price)}</div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
