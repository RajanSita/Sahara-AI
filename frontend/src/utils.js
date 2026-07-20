export const STATUS_LABELS = {
  not_started: 'Not Started',
  awaiting_approval: 'Awaiting Approval',
  sent: 'Sent',
  completed: 'Completed',
  rejected: 'Rejected',
}

export const INSTITUTION_ICONS = {
  government: '🏛️',
  bank: '🏦',
  insurance: '🛡️',
  employer: '🏢',
  property: '🏠',
}

export const INSTITUTION_COLORS = {
  government: '#7C9DC4',
  bank:       '#C9A84C',
  insurance:  '#8A7CC4',
  employer:   '#5C8A6E',
  property:   '#C47C7C',
}

export function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}

export function groupTasksByType(tasks) {
  return tasks.reduce((acc, task) => {
    const key = task.institution_type
    if (!acc[key]) acc[key] = []
    acc[key].push(task)
    return acc
  }, {})
}
