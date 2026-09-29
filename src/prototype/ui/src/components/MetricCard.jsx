function MetricCard({ value, label, tone = 'navy' }) {
  return <article className={`metric-card metric-card--${tone}`}><p className="metric-card__value">{value}</p><h3>{label}</h3></article>;
}
export default MetricCard;
