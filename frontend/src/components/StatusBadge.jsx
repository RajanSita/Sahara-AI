import { STATUS_LABELS } from '../utils'

export default function StatusBadge({ status }) {
  return (
    <span className={`badge badge-${status}`}>
      <span>{dot(status)}</span>
      {STATUS_LABELS[status] || status}
    </span>
  )
}

function dot(status) {
  const colors = {
    not_started:        '#8899AA',
    awaiting_approval:  '#C9A84C',
    sent:               '#7CAE8E',
    completed:          '#A8E4BC',
    rejected:           '#F08080',
  }
  return (
    <span style={{
      display: 'inline-block',
      width: 6, height: 6,
      borderRadius: '50%',
      background: colors[status] || '#888',
      flexShrink: 0,
    }} />
  )
}
