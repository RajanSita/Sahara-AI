import { Link } from 'react-router-dom'

const SDG_CARDS = [
  {
    num: '1', label: 'No Poverty',
    desc: 'Prevents loss of entitled financial claims — insurance, PF, bank accounts.',
    color: '#E5243B', icon: '🏛️'
  },
  {
    num: '5', label: 'Gender Equality',
    desc: 'Restores financial agency to widows who disproportionately lose asset access.',
    color: '#FF3A21', icon: '⚖️'
  },
  {
    num: '16', label: 'Strong Institutions',
    desc: 'Reduces exploitation by informal "fixers". Fair access to legal processes.',
    color: '#00689D', icon: '🕊️'
  },
]

const FEATURES = [
  { icon: '🤖', title: 'Multi-Agent AI', desc: '6 specialized agents that classify, prioritize, and draft every required letter.' },
  { icon: '🛡️', title: 'Human-in-the-Loop', desc: 'Nothing is ever sent without your explicit approval. You stay in control.' },
  { icon: '📋', title: 'Complete Task Tracking', desc: 'From "Not Started" through "Sent" to "Completed" — one dashboard for everything.' },
  { icon: '🔔', title: 'Auto Follow-Ups', desc: 'Politely follows up with institutions that haven\'t responded in 14 days.' },
  { icon: '📄', title: 'Ready-to-Send Drafts', desc: 'Professionally drafted letters for banks, insurers, government offices, employers.' },
  { icon: '🌐', title: 'India-First Design', desc: 'Built for Indian institutional processes: EPFO, succession certificates, mutation.' },
]

export default function Landing() {
  return (
    <div>
      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section style={{
        minHeight: '88vh',
        display: 'flex', alignItems: 'center',
        background: `
          radial-gradient(ellipse 80% 60% at 50% 0%, rgba(201,168,76,0.08) 0%, transparent 70%),
          radial-gradient(ellipse 60% 40% at 80% 80%, rgba(92,138,110,0.06) 0%, transparent 60%)
        `,
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Decorative lines */}
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'repeating-linear-gradient(0deg, transparent, transparent 59px, rgba(255,255,255,0.018) 60px)',
        }} />

        <div className="page-container" style={{ textAlign: 'center', padding: '80px 24px' }}>
          <div className="animate-fade-in-up">
            <div style={{
              display: 'inline-block',
              padding: '6px 18px',
              background: 'rgba(201,168,76,0.1)',
              border: '1px solid rgba(201,168,76,0.25)',
              borderRadius: '20px',
              fontSize: '0.78rem', fontWeight: 600,
              letterSpacing: '0.08em',
              color: 'var(--gold)',
              textTransform: 'uppercase',
              marginBottom: 28,
            }}>
              AI for Social Good 
            </div>

            <h1 style={{
              fontFamily: "'Cormorant Garamond', serif",
              fontSize: 'clamp(3rem, 7vw, 5.5rem)',
              fontWeight: 700,
              lineHeight: 1.08,
              margin: '0 0 24px',
              letterSpacing: '-0.02em',
            }}>
              When grief shouldn't<br />
              <span style={{ color: 'var(--gold)' }}>mean paperwork.</span>
            </h1>

            <p style={{
              fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
              color: 'var(--text-muted)',
              maxWidth: 600,
              margin: '0 auto 40px',
              lineHeight: 1.8,
            }}>
              Sahara.ai identifies every administrative task a family must complete after a death,
              drafts every letter, and tracks every response — while you remain in control of everything.
            </p>

            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link to="/intake" className="btn-primary" style={{ fontSize: '1rem', padding: '14px 36px' }}>
                Start a New Case →
              </Link>
              <Link to="/cases" className="btn-secondary" style={{ fontSize: '1rem', padding: '14px 36px' }}>
                View Cases
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── How it works ─────────────────────────────────────────────────── */}
      <section style={{ padding: '80px 24px', background: 'rgba(255,255,255,0.02)' }}>
        <div className="page-container">
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <h2 className="section-title">How Sahara.ai Works</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: 12, fontSize: '1.05rem' }}>
              Six AI agents working together, all under your control.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 20,
          }}>
            {FEATURES.map((f, i) => (
              <div key={i} className="glass-card" style={{ padding: 28 }}>
                <div style={{ fontSize: '2rem', marginBottom: 14 }}>{f.icon}</div>
                <h3 style={{
                  fontFamily: "'Cormorant Garamond', serif",
                  fontSize: '1.25rem', fontWeight: 600,
                  margin: '0 0 10px',
                }}>{f.title}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: 1.7, margin: 0 }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Process Steps ────────────────────────────────────────────────── */}
      <section style={{ padding: '80px 24px' }}>
        <div className="page-container">
          <h2 className="section-title" style={{ textAlign: 'center', marginBottom: 56 }}>
            What happens when you submit
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {[
              ['1', 'You fill the intake form', 'Share the deceased\'s details, banks, insurers, employer, and family contact.'],
              ['2', 'AI identifies every task', 'The classifier and priority agents produce a ranked list of all institutional actions required.'],
              ['3', 'Letters are drafted for you', 'The drafting agent writes ready-to-review letters for every bank, insurer, government office, and employer.'],
              ['4', 'You review and approve', 'Read each draft, edit if needed, then approve. Nothing is sent without your say.'],
              ['5', 'AI follows up for you', 'If an institution doesn\'t respond in 14 days, a follow-up is drafted and queued for your approval.'],
            ].map(([num, title, desc], i, arr) => (
              <div key={i} style={{ display: 'flex', gap: 24, position: 'relative' }}>
                {/* Step number + line */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
                  <div style={{
                    width: 44, height: 44, borderRadius: '50%',
                    background: 'linear-gradient(135deg, var(--gold), var(--gold-light))',
                    color: 'var(--navy)', fontWeight: 700, fontSize: '1rem',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>{num}</div>
                  {i < arr.length - 1 && (
                    <div style={{ width: 1, flex: 1, minHeight: 40, background: 'var(--glass-border)', margin: '8px 0' }} />
                  )}
                </div>
                {/* Content */}
                <div style={{ paddingBottom: i < arr.length - 1 ? 32 : 0, paddingTop: 8 }}>
                  <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: 6 }}>{title}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: 1.7 }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SDG Section ──────────────────────────────────────────────────── */}
      <section style={{ padding: '80px 24px', background: 'rgba(255,255,255,0.02)' }}>
        <div className="page-container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2 className="section-title">UN Sustainable Development Goals</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: 12 }}>
              Designed to advance social justice where institutions fail the most vulnerable.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
            {SDG_CARDS.map(sdg => (
              <div key={sdg.num} className="glass-card" style={{ padding: 28, borderTop: `3px solid ${sdg.color}` }}>
                <div style={{ fontSize: '2rem', marginBottom: 12 }}>{sdg.icon}</div>
                <div style={{ color: sdg.color, fontWeight: 700, fontSize: '0.75rem', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6 }}>
                  SDG {sdg.num}
                </div>
                <h3 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '1.2rem', margin: '0 0 10px' }}>
                  {sdg.label}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.87rem', lineHeight: 1.7, margin: 0 }}>{sdg.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────── */}
      <section style={{ padding: '80px 24px', textAlign: 'center' }}>
        <div className="page-container">
          <div className="glass-card" style={{ padding: '60px 40px', maxWidth: 700, margin: '0 auto' }}>
            <h2 className="section-title" style={{ marginBottom: 16 }}>Ready to begin?</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: 36, fontSize: '1.05rem', lineHeight: 1.8 }}>
              Fill in a few details about the deceased and their assets. The AI will handle the rest.
            </p>
            <Link to="/intake" className="btn-primary" style={{ fontSize: '1rem', padding: '16px 44px' }}>
              Start a New Case →
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────────────────────── */}
      <footer style={{
        padding: '32px 24px',
        borderTop: '1px solid var(--glass-border)',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.82rem',
      }}>
        <p style={{ margin: 0 }}>
          Sahara.ai - Created By Rajan, Ayushi Kapoor and Gagan Jha
          <br/>
          <span style={{ opacity: 0.5 }}>AICTE AI Automation and Intelligent Solutions-  AI Automation and Intelligent Solutions</span>
        </p>
      </footer>
    </div>
  )
}
