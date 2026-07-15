import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";

const tooltipStyle = {
  backgroundColor: "#111527",
  border: "1px solid rgba(108,99,255,0.3)",
  borderRadius: 8,
  fontSize: 12,
  color: "#F0F2FF",
};

function fmtAxis(v) {
  return "₹" + v.toLocaleString("en-IN");
}

/** Line chart: avg/min/max price over time */
export function HistoryLineChart({ points }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={points} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
        <XAxis dataKey="label" stroke="#555B7A" fontSize={11} tickLine={false} axisLine={false} />
        <YAxis stroke="#555B7A" fontSize={11} tickFormatter={fmtAxis} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v) => fmtAxis(v)} />
        <Line type="monotone" dataKey="avg" stroke="#6C63FF" strokeWidth={2} dot={false} name="Avg Price" />
        <Line type="monotone" dataKey="min" stroke="#FF6584" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="Min Price" />
        <Line type="monotone" dataKey="max" stroke="#43D9A5" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="Max Price" />
      </LineChart>
    </ResponsiveContainer>
  );
}

/** Bar chart: price by day of week, cheapest/priciest highlighted */
export function DayOfWeekChart({ days, prices }) {
  const data = days.map((d, i) => ({ day: d, price: prices[i] }));
  const min = Math.min(...prices), max = Math.max(...prices);
  const colorFor = (p) => (p === min ? "#43D9A5" : p === max ? "#FF6584" : "#6C63FF");

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
        <XAxis dataKey="day" stroke="#555B7A" fontSize={11} tickLine={false} axisLine={false} />
        <YAxis stroke="#555B7A" fontSize={11} tickFormatter={fmtAxis} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v) => fmtAxis(v)} />
        <Bar dataKey="price" radius={[8, 8, 0, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={colorFor(d.price)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Bar chart: price per airline */
export function AirlineChart({ airlines, prices }) {
  const palette = ["#6C63FF", "#FF6584", "#FFB347", "#43D9A5", "#38BDF8"];
  const data = airlines.map((a, i) => ({ airline: a, price: prices[i], fill: palette[i % palette.length] }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
        <XAxis dataKey="airline" stroke="#555B7A" fontSize={10} tickLine={false} axisLine={false} />
        <YAxis stroke="#555B7A" fontSize={11} tickFormatter={fmtAxis} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v) => fmtAxis(v)} />
        <Bar dataKey="price" radius={[8, 8, 0, 0]}>
          {data.map((d, i) => <Cell key={i} fill={d.fill} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
