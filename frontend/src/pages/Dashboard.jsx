import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCase, getCaseTasks, getCaseStats } from '../api'
import TaskCard from '../components/TaskCard'
import StatusBadge from '../components/StatusBadge'
import { INSTITUTION_ICONS, groupTasksByType, formatDate } from '../utils'

const TYPE_LABELS = {
  government: 'Government & Legal',
  bank: 'Banking & Financial',
  insurance: 'Insurance',
  employer: 'Employment',
  property: 'Property',
}

export default function Dashboard() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState(null)
  const [tasks, setTasks] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState('all')

  const load = async () => {
    try {
      const [cRes, tRes, sRes] = await Promise.all([
        getCase(caseId),
        getCaseTasks(caseId),
        getCaseStats(caseId),
      ])
      setCaseData(cRes.data)
      setTasks(tRes.data)
      setStats(sRes.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [caseId])

  const filteredTasks = activeFilter === 'all'
    ? tasks
    : tasks.filter(t => t.status === activeFilter)

  const grouped = groupTasksByType(filteredTasks)

  if (loading) return (
    <div style={{ padding: '80px 24px', textAlign: 'center' }}>
      <div className="animate-pulse-soft" style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
        Loading case…
      </div>
    </div>
  )

  if (!caseData) return (
    <div style={{ padding: '80px 24px', textAlign: 'center' }}>
      <p className="text-muted">Case not found.</p>
      <button className="btn-primary" onClick={() => navigate('/cases')} style={{ marginTop: 16 }}>
        View All Cases
      </button>
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', padding: '40px 24px' }}>
      <div className="page-container">

        {/* ── Breadcrumb ───────────────────────────────────────────────────── */}
        <div style={{ marginBottom: 24 }}>
          <button
            onClick={() => navigate('/cases')}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--text-muted)', fontSize: '0.85rem',
              display: 'flex', alignItems: 'center', gap: 6, padding: 0,
              transition: 'color 0.2s',
            }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--gold)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            ← All Cases
          </button>
        </div>

        {/* ── Case Header ────────────────────────────────────────────────── */}
        <div className="glass-card" style={{ padding: '28px 32px', marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
                Case File
              </div>
              <h1 style={{
                fontFamily: "'Cormorant Garamond', serif",
                fontSize: '2rem', margin: '0 0 6px',
              }}>
                Late {caseData.deceased_name}
              </h1>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.88rem', display: 'flex', gap: 20, flexWrap: 'wrap' }}>
                <span>📅 {formatDate(caseData.date_of_death)}</span>
                {caseData.place_of_death && <span>📍 {caseData.place_of_death}</span>}
                {caseData.family_contact_name && (
                  <span>👤 {caseData.family_contact_name} ({caseData.family_contact_relation})</span>
                )}
              </div>
            </div>

            {/* Progress ring area */}
            {stats && (
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '2.4rem', fontWeight: 700,
                  fontFamily: "'Cormorant Garamond', serif",
                  color: stats.progress_pct === 100 ? 'var(--sage-light)' : 'var(--gold)',
                }}>
                  {stats.progress_pct}%
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Complete</div>
              </div>
            )}
          </div>

          {/* Stats bar */}
          {stats && (
            <div style={{ marginTop: 24 }}>
              {/* Progress bar */}
              <div style={{
                height: 6, borderRadius: 3,
                background: 'rgba(255,255,255,0.08)',
                overflow: 'hidden', marginBottom: 16,
              }}>
                <div style={{
                  height: '100%', borderRadius: 3,
                  width: `${stats.progress_pct}%`,
                  background: 'linear-gradient(90deg, var(--sage), var(--sage-light))',
                  transition: 'width 0.5s ease',
                }} />
              </div>

              <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
                {[
                  ['Total', stats.total, '#A8B4C8'],
                  ['Awaiting Approval', stats.awaiting_approval, 'var(--gold)'],
                  ['Sent', stats.sent, 'var(--sage-light)'],
                  ['Completed', stats.completed, '#A8E4BC'],
                ].map(([label, val, color]) => (
                  <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: '1.1rem', fontWeight: 700, color }}>{val}</span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Filter Tabs ──────────────────────────────────────────────── */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 28, flexWrap: 'wrap' }}>
          {[
            ['all', 'All Tasks'],
            ['not_started', '📋 Not Started'],
            ['awaiting_approval', '⏳ Needs Review'],
            ['sent', '✉️ Sent'],
            ['completed', '✅ Completed'],
          ].map(([val, label]) => (
            <button key={val} onClick={() => setActiveFilter(val)} style={{
              padding: '7px 16px', borderRadius: 20, fontSize: '0.82rem', fontWeight: 500,
              cursor: 'pointer', transition: 'all 0.2s',
              background: activeFilter === val ? 'rgba(201,168,76,0.12)' : 'transparent',
              color: activeFilter === val ? 'var(--gold)' : 'var(--text-muted)',
              border: activeFilter === val ? '1px solid rgba(201,168,76,0.25)' : '1px solid var(--glass-border)',
            }}>
              {label} {val !== 'all' && stats ? `(${stats[val] ?? 0})` : val === 'all' && stats ? `(${stats.total})` : ''}
            </button>
          ))}
        </div>

        {/* ── Task Groups ──────────────────────────────────────────────── */}
        {Object.keys(TYPE_LABELS).map(type => {
          const typeTasks = grouped[type]
          if (!typeTasks?.length) return null
          return (
            <div key={type} style={{ marginBottom: 36 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <span style={{ fontSize: '1.2rem' }}>{INSTITUTION_ICONS[type]}</span>
                <h2 style={{
                  fontFamily: "'Cormorant Garamond', serif",
                  fontSize: '1.2rem', fontWeight: 600, margin: 0,
                }}>
                  {TYPE_LABELS[type]}
                </h2>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: 4 }}>
                  ({typeTasks.length})
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {typeTasks.map(task => (
                  <TaskCard key={task.id} task={task} caseId={caseId} onStatusChange={load} />
                ))}
              </div>
            </div>
          )
        })}

        {filteredTasks.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 24px', color: 'var(--text-muted)' }}>
            No tasks in this category.
          </div>
        )}
      </div>
    </div>
  )
}
