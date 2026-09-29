import { useId } from 'react';

function DataTable({ caption, columns, rows }) {
  const captionId = useId();
  return <div className="table-wrap" role="region" aria-labelledby={caption ? captionId : undefined} tabIndex="0">
    {caption && <p className="table-caption" id={captionId}>{caption}</p>}
    <table>
      <thead><tr>{columns.map((column) => <th key={column.key} scope="col">{column.label}</th>)}</tr></thead>
      <tbody>{rows.map((row, index) => <tr key={row.id ?? index}>{columns.map((column) => <td key={column.key}>{row[column.key]}</td>)}</tr>)}</tbody>
    </table>
  </div>;
}
export default DataTable;
