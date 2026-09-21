const colors = { navy: '#102b4e', turquoise: '#087e8b', amber: '#a85d00', red: '#b23a31', gray: '#8a8885' };
function LineChart({ series, label }) {
  const max = Math.max(...series.flatMap((item) => item.values), 1);
  const points = (values) => values.map((value, i) => `${28 + i * 100.8},${174 - (value / max) * 140}`).join(' ');
  return <div className="chart" role="img" aria-label={label}><svg viewBox="0 0 560 200" preserveAspectRatio="none">{[34, 69, 104, 139, 174].map((y) => <line className="chart__grid" x1="28" y1={y} x2="532" y2={y} key={y} />)}{series.map((item) => <polyline className="chart__line" key={item.name} points={points(item.values)} stroke={colors[item.tone]} />)}</svg><div className="chart__legend">{series.map((item) => <span key={item.name}><i style={{ background: colors[item.tone] }} />{item.name}</span>)}</div></div>;
}
function BarChart({ rows, label }) {
  const max = Math.max(...rows.flatMap((row) => row.values.map((item) => item.value)), 1);
  return <div className="bar-chart" role="img" aria-label={label}>{rows.map((row) => <div className="bar-chart__row" key={row.label}><span>{row.label}</span><div>{row.values.map((item) => <div className="bar-chart__bar-line" key={item.name}><p><i style={{ width: `${item.value / max * 100}%`, background: colors[item.tone] }} /></p><b>{item.value}{item.suffix ?? ''}</b></div>)}</div></div>)}</div>;
}
export { BarChart, LineChart };
