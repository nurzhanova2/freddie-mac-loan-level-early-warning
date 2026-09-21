function DataTable({ caption, columns, rows }) {
  return <div className="table-wrap">{caption && <p className="table-caption">{caption}</p>}<table><thead><tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={row.id ?? i}>{columns.map((c) => <td key={c.key}>{row[c.key]}</td>)}</tr>)}</tbody></table></div>;
}
export default DataTable;
