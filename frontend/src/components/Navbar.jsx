import { Link, useLocation } from 'react-router-dom'

export default function Navbar({ user, onLogout }) {
  const location = useLocation()

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'rgba(15,28,63,0.90)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.07)',
    }}>
      <div className="page-container" style={{
        display: 'flex', alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 24px',
      }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
          <img
            src="/logo.png"
            alt="Sahara.ai"
            style={{ height: 36, width: 'auto', objectFit: 'contain' }}
            onError={e => { e.currentTarget.style.display = 'none' }}
          />
          <span style={{
            fontFamily: "'Cormorant Garamond', serif",
            fontSize: '1.35rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            letterSpacing: '0.02em',
          }}>
            Sahara<span style={{ color: 'var(--gold)' }}>.ai</span>
          </span>
        </Link>

        {/* Nav links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <NavLink to="/" label="Home" active={location.pathname === '/'} />

          {user ? (
            <>
              <NavLink to="/intake" label="New Case" active={location.pathname === '/intake'} />
              <NavLink to="/cases" label="Cases" active={location.pathname.startsWith('/cases')} />
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginLeft: 12, paddingLeft: 12, borderLeft: '1px solid rgba(255,255,255,0.1)' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--gold)', fontWeight: 600 }}>
                  👤 {user.name}
                </span>
                <button onClick={onLogout} style={{
                  background: 'rgba(220,80,80,0.12)', border: '1px solid rgba(220,80,80,0.3)',
                  color: '#F08080', borderRadius: 20, padding: '5px 12px', fontSize: '0.78rem',
                  cursor: 'pointer', fontWeight: 500,
                }}>
                  Logout
                </button>
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 8 }}>
              <button onClick={() => window.location.href = '/api/auth/google'} style={{
                padding: '7px 16px', borderRadius: '20px', fontSize: '0.82rem',
                fontWeight: 600, border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(255,255,255,0.06)',
                color: 'var(--text-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
                transition: 'all 0.2s',
              }}>
                <span>🌐</span> Sign in with Google
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}

function NavLink({ to, label, active }) {
  return (
    <Link to={to} style={{
      padding: '7px 16px',
      borderRadius: '20px',
      fontSize: '0.85rem',
      fontWeight: 500,
      textDecoration: 'none',
      transition: 'all 0.2s',
      background: active ? 'rgba(201,168,76,0.12)' : 'transparent',
      color: active ? 'var(--gold)' : 'var(--text-muted)',
      border: active ? '1px solid rgba(201,168,76,0.25)' : '1px solid transparent',
    }}>
      {label}
    </Link>
  )
}
