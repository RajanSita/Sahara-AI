import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { listCases, getCaseStats } from '../api'
import { formatDate } from '../utils'

export default function Cases() {
  const navigate = useNavigate()
  const [cases, setCases] = useState([])
  const [statsMap, setStatsMap] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listCases().then(async res => {
      const cases = res.data
      setCases(cases)
      // Load stats for each case
      const statsEntries = await Promise.all(
        cases.map(c => getCaseStats(c.id).then(r => [c.id, r.data]).catch(() => [c.id, null]))
      )
      setStatsMap(Object.fromEntries(statsEntries))
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: '80px 24px', textAlign: 'center' }}>
      <div className="animate-pulse-soft" style={{ color: 'var(--text-muted)' }}>Loading cases…</div>
    </div>
  )

  return (
    <div style={{ minHeight: '100vh', padding: '40px 24px' }}>
      <div className="page-container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 36, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
              All Cases
            </div>
            <h1 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '2.2rem', margin: 0 }}>
              Case Files
            </h1>
          </div>
          <button className="btn-primary" onClick={() => navigate('/intake')}>+ New Case</button>
        </div>

        {cases.length === 0 ? (
          <div className="glass-card" style={{ padding: '60px 40px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: 16 }}>📁</div>
            <h2 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '1.6rem', marginBottom: 12 }}>No cases yet</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: 28 }}>Start by creating a new case for a recently deceased person.</p>
            <button className="btn-primary" onClick={() => navigate('/intake')}>Start a New Case</button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {cases.map(c => {
              const stats = statsMap[c.id]
              return (
                <div key={c.id} className="glass-card-solid"
                  onClick={() => navigate(`/cases/${c.id}`)}
                  style={{
                    padding: '22px 26px', cursor: 'pointer',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.3)' }}
                  onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'none' }}
                >
                  <div style={{
                    width: 48, height: 48, borderRadius: 12,
                    background: 'rgba(201,168,76,0.1)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.3rem', flexShrink: 0,
                  }}>🕊️</div>

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '1.2rem', fontWeight: 600 }}>
                      Late {c.deceased_name}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 3 }}>
                      {formatDate(c.date_of_death)}
                      {c.family_contact_name && ` · Contact: ${c.family_contact_name}`}
                    </div>
                  </div>

                  {stats && (
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <div style={{ fontSize: '1.4rem', fontWeight: 700, color: stats.progress_pct === 100 ? 'var(--sage-light)' : 'var(--gold)' }}>
                        {stats.progress_pct}%
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {stats.completed}/{stats.total} done
                      </div>
                    </div>
                  )}

                  <span style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>›</span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
