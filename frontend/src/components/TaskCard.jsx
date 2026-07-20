import { useNavigate } from 'react-router-dom'
import StatusBadge from './StatusBadge'
import { INSTITUTION_ICONS, INSTITUTION_COLORS } from '../utils'

export default function TaskCard({ task, caseId, onStatusChange }) {
  const navigate = useNavigate()
  const icon = INSTITUTION_ICONS[task.institution_type] || '📋'
  const color = INSTITUTION_COLORS[task.institution_type] || '#888'

  return (
    <div
      className="glass-card-solid"
      onClick={() => navigate(`/cases/${caseId}/tasks/${task.id}`)}
      style={{
        padding: '18px 20px',
        cursor: 'pointer',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease',
        borderLeft: `3px solid ${color}`,
        display: 'flex',
        alignItems: 'center',
        gap: 16,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateX(4px)'
        e.currentTarget.style.boxShadow = `0 4px 20px rgba(0,0,0,0.3)`
        e.currentTarget.style.borderColor = color
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = 'translateX(0)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {/* Icon */}
      <div style={{
        width: 44, height: 44, borderRadius: 10,
        background: `${color}20`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '1.3rem', flexShrink: 0,
      }}>
        {icon}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontWeight: 600, fontSize: '0.92rem',
          color: 'var(--text-primary)',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>
          {task.task_type}
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 3 }}>
          {task.institution_name}
        </div>
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6, flexShrink: 0 }}>
        <StatusBadge status={task.status} />
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Priority #{task.priority_rank}
        </span>
      </div>
    </div>
  )
}
