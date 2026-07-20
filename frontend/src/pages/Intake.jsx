import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCase } from '../api'

const STEPS = ['Deceased Details', 'Financial Accounts', 'Employment & Property', 'Family Contact']

const EMPTY_BANK = { bank_name: '', account_type: 'savings', branch: '', has_nominee: true }
const EMPTY_INSURER = { insurer_name: '', policy_type: 'life', policy_number: '', nominee: '' }
const EMPTY_EMPLOYER = { employer_name: '', designation: '', has_pf: true, has_gratuity: true }
const EMPTY_PROPERTY = { description: '', location: '' }
const EMPTY_MEMBER = { name: '', relation: 'spouse', is_primary_contact: true, phone: '', email: '' }

const AI_STEPS = [
  { label: 'Parsing intake details…', icon: '📋', delay: 0 },
  { label: 'Classifying required tasks…', icon: '🤖', delay: 4000 },
  { label: 'Prioritising by urgency…', icon: '⚡', delay: 10000 },
  { label: 'Drafting letters for each institution…', icon: '✍️', delay: 16000 },
  { label: 'Finalising case file…', icon: '🕊️', delay: 50000 },
]

function ProcessingOverlay() {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    const timers = AI_STEPS.map((s, i) =>
      setTimeout(() => setActiveStep(i), s.delay)
    )
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: 'rgba(10, 18, 45, 0.97)',
      backdropFilter: 'blur(20px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexDirection: 'column',
    }}>
      {/* Animated glow */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse 60% 40% at 50% 40%, rgba(201,168,76,0.07) 0%, transparent 70%)',
      }} />

      <div style={{ textAlign: 'center', maxWidth: 480, padding: '0 32px', position: 'relative' }}>
        {/* Pulsing icon */}
        <div style={{
          fontSize: '3.5rem', marginBottom: 28,
          animation: 'pulse-soft 2s ease-in-out infinite',
        }}>
          {AI_STEPS[activeStep].icon}
        </div>

        <h2 style={{
          fontFamily: "'Cormorant Garamond', serif",
          fontSize: '2rem', margin: '0 0 12px',
          color: 'var(--text-primary)',
        }}>
          AI Agents Working…
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: 40, lineHeight: 1.7 }}>
          Our 6 specialised agents are analysing the case, identifying every required task, and drafting letters for each institution.
        </p>

        {/* Step list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, textAlign: 'left' }}>
          {AI_STEPS.map((s, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 14,
              padding: '12px 18px', borderRadius: 12,
              background: i === activeStep
                ? 'rgba(201,168,76,0.1)'
                : i < activeStep ? 'rgba(92,138,110,0.08)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${i === activeStep ? 'rgba(201,168,76,0.25)' : i < activeStep ? 'rgba(92,138,110,0.2)' : 'rgba(255,255,255,0.06)'}`,
              transition: 'all 0.5s ease',
              opacity: i > activeStep ? 0.4 : 1,
            }}>
              <span style={{ fontSize: '1.2rem', flexShrink: 0 }}>
                {i < activeStep ? '✅' : s.icon}
              </span>
              <span style={{
                fontSize: '0.88rem', fontWeight: i === activeStep ? 600 : 400,
                color: i === activeStep ? 'var(--gold)' : i < activeStep ? 'var(--sage-light)' : 'var(--text-muted)',
              }}>
                {s.label}
              </span>
              {i === activeStep && (
                <span style={{
                  marginLeft: 'auto', fontSize: '0.75rem',
                  color: 'var(--gold)', animation: 'pulse-soft 1.5s infinite',
                }}>
                  ●
                </span>
              )}
            </div>
          ))}
        </div>

        <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: 28, opacity: 0.6 }}>
          This typically takes 30–60 seconds. Please don't close this tab.
        </p>
      </div>
    </div>
  )
}

export default function Intake() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({
    deceased_name: '', date_of_death: '', place_of_death: '', religion: '',
    death_certificate_obtained: false,
    banks: [],
    insurance_policies: [],
    employers: [],
    properties: [],
    family_members: [{ ...EMPTY_MEMBER }],
  })

  const update = (field, value) => setForm(f => ({ ...f, [field]: value }))

  const addItem = (field, template) => setForm(f => ({ ...f, [field]: [...f[field], { ...template }] }))
  const removeItem = (field, i) => setForm(f => ({ ...f, [field]: f[field].filter((_, idx) => idx !== i) }))
  const updateItem = (field, i, key, value) => setForm(f => ({
    ...f,
    [field]: f[field].map((item, idx) => idx === i ? { ...item, [key]: value } : item)
  }))

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await createCase(form)
      navigate(`/cases/${res.data.case.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please check the backend is running.')
      setLoading(false)
    }
  }

  const canNext = () => {
    if (step === 0) return form.deceased_name.trim() && form.date_of_death
    return true
  }

  return (
    <>
      {/* AI Processing overlay — shown while backend pipeline runs */}
      {loading && <ProcessingOverlay />}

      <div style={{ minHeight: '100vh', padding: '40px 24px' }}>
        <div style={{ maxWidth: 720, margin: '0 auto' }}>


        {/* Header */}
        <div style={{ marginBottom: 40 }}>
          <div className="text-muted" style={{ fontSize: '0.82rem', marginBottom: 8 }}>New Case</div>
          <h1 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '2.4rem', margin: 0 }}>
            Case Intake Form
          </h1>
          <p className="text-muted" style={{ marginTop: 8, fontSize: '0.95rem' }}>
            Tell us about the deceased and their accounts. The AI will do the rest.
          </p>
        </div>

        {/* Step Progress */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 40, flexWrap: 'wrap' }}>
          {STEPS.map((label, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '7px 14px', borderRadius: 20,
                background: i === step ? 'rgba(201,168,76,0.12)' : i < step ? 'rgba(92,138,110,0.12)' : 'rgba(255,255,255,0.04)',
                border: `1px solid ${i === step ? 'rgba(201,168,76,0.3)' : i < step ? 'rgba(92,138,110,0.3)' : 'rgba(255,255,255,0.08)'}`,
                cursor: i < step ? 'pointer' : 'default',
                transition: 'all 0.2s',
              }} onClick={() => i < step && setStep(i)}>
                <div style={{
                  width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
                  background: i === step ? 'var(--gold)' : i < step ? 'var(--sage)' : 'rgba(255,255,255,0.1)',
                  color: i <= step ? 'white' : 'var(--text-muted)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.7rem', fontWeight: 700,
                }}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span style={{
                  fontSize: '0.78rem', fontWeight: 500,
                  color: i === step ? 'var(--gold)' : i < step ? 'var(--sage-light)' : 'var(--text-muted)',
                }}>{label}</span>
              </div>
              {i < STEPS.length - 1 && <div style={{ width: 16, height: 1, background: 'var(--glass-border)' }} />}
            </div>
          ))}
        </div>

        {/* Form Card */}
        <div className="glass-card-solid" style={{ padding: 36 }}>

          {/* ── Step 0: Deceased Details ──── */}
          {step === 0 && (
            <div className="animate-fade-in">
              <SectionTitle>About the Deceased</SectionTitle>
              <Row>
                <Field label="Full Name *">
                  <input className="form-input" placeholder="e.g. Rajesh Kumar Sharma"
                    value={form.deceased_name} onChange={e => update('deceased_name', e.target.value)} />
                </Field>
                <Field label="Date of Death *">
                  <input className="form-input" type="date"
                    value={form.date_of_death} onChange={e => update('date_of_death', e.target.value)} />
                </Field>
              </Row>
              <Row>
                <Field label="Place of Death">
                  <input className="form-input" placeholder="e.g. AIIMS, New Delhi"
                    value={form.place_of_death} onChange={e => update('place_of_death', e.target.value)} />
                </Field>
                <Field label="Religion">
                  <select className="form-input" value={form.religion} onChange={e => update('religion', e.target.value)}>
                    <option value="">Select (optional)</option>
                    <option>Hindu</option><option>Muslim</option><option>Christian</option>
                    <option>Sikh</option><option>Buddhist</option><option>Jain</option><option>Other</option>
                  </select>
                </Field>
              </Row>
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 16, cursor: 'pointer' }}>
                <input type="checkbox" checked={form.death_certificate_obtained}
                  onChange={e => update('death_certificate_obtained', e.target.checked)}
                  style={{ width: 16, height: 16, accentColor: 'var(--gold)' }} />
                <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                  Death certificate has already been obtained
                </span>
              </label>
            </div>
          )}

          {/* ── Step 1: Financial Accounts ──── */}
          {step === 1 && (
            <div className="animate-fade-in">
              <SectionTitle>Bank Accounts</SectionTitle>
              {form.banks.map((bank, i) => (
                <div key={i} className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>Bank #{i + 1}</span>
                    <button onClick={() => removeItem('banks', i)} style={{ background: 'none', border: 'none', color: '#F08080', cursor: 'pointer', fontSize: '0.85rem' }}>Remove</button>
                  </div>
                  <Row>
                    <Field label="Bank Name">
                      <input className="form-input" placeholder="e.g. State Bank of India"
                        value={bank.bank_name} onChange={e => updateItem('banks', i, 'bank_name', e.target.value)} />
                    </Field>
                    <Field label="Account Type">
                      <select className="form-input" value={bank.account_type} onChange={e => updateItem('banks', i, 'account_type', e.target.value)}>
                        <option value="savings">Savings</option>
                        <option value="current">Current</option>
                        <option value="joint">Joint</option>
                        <option value="locker">Safe Deposit Locker</option>
                      </select>
                    </Field>
                  </Row>
                  <Field label="Branch (optional)">
                    <input className="form-input" placeholder="e.g. Connaught Place, New Delhi"
                      value={bank.branch} onChange={e => updateItem('banks', i, 'branch', e.target.value)} />
                  </Field>
                </div>
              ))}
              <button className="btn-ghost" onClick={() => addItem('banks', EMPTY_BANK)}>+ Add Bank Account</button>

              <div className="divider" />

              <SectionTitle>Insurance Policies</SectionTitle>
              {form.insurance_policies.map((pol, i) => (
                <div key={i} className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>Policy #{i + 1}</span>
                    <button onClick={() => removeItem('insurance_policies', i)} style={{ background: 'none', border: 'none', color: '#F08080', cursor: 'pointer', fontSize: '0.85rem' }}>Remove</button>
                  </div>
                  <Row>
                    <Field label="Insurer Name">
                      <input className="form-input" placeholder="e.g. LIC of India"
                        value={pol.insurer_name} onChange={e => updateItem('insurance_policies', i, 'insurer_name', e.target.value)} />
                    </Field>
                    <Field label="Policy Type">
                      <select className="form-input" value={pol.policy_type} onChange={e => updateItem('insurance_policies', i, 'policy_type', e.target.value)}>
                        <option value="life">Life Insurance</option>
                        <option value="health">Health Insurance</option>
                        <option value="vehicle">Vehicle Insurance</option>
                        <option value="other">Other</option>
                      </select>
                    </Field>
                  </Row>
                  <Field label="Policy Number (if known)">
                    <input className="form-input" placeholder="e.g. 123456789"
                      value={pol.policy_number} onChange={e => updateItem('insurance_policies', i, 'policy_number', e.target.value)} />
                  </Field>
                </div>
              ))}
              <button className="btn-ghost" onClick={() => addItem('insurance_policies', EMPTY_INSURER)}>+ Add Insurance Policy</button>
            </div>
          )}

          {/* ── Step 2: Employment & Property ──── */}
          {step === 2 && (
            <div className="animate-fade-in">
              <SectionTitle>Employers</SectionTitle>
              {form.employers.map((emp, i) => (
                <div key={i} className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>Employer #{i + 1}</span>
                    <button onClick={() => removeItem('employers', i)} style={{ background: 'none', border: 'none', color: '#F08080', cursor: 'pointer', fontSize: '0.85rem' }}>Remove</button>
                  </div>
                  <Row>
                    <Field label="Employer Name">
                      <input className="form-input" placeholder="e.g. Ministry of Railways"
                        value={emp.employer_name} onChange={e => updateItem('employers', i, 'employer_name', e.target.value)} />
                    </Field>
                    <Field label="Designation">
                      <input className="form-input" placeholder="e.g. Station Master"
                        value={emp.designation} onChange={e => updateItem('employers', i, 'designation', e.target.value)} />
                    </Field>
                  </Row>
                  <div style={{ display: 'flex', gap: 24, marginTop: 10 }}>
                    {[['has_pf', 'Has PF / EPF'], ['has_gratuity', 'Has Gratuity']].map(([key, label]) => (
                      <label key={key} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                        <input type="checkbox" checked={emp[key]} onChange={e => updateItem('employers', i, key, e.target.checked)}
                          style={{ width: 15, height: 15, accentColor: 'var(--gold)' }} />
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
              <button className="btn-ghost" onClick={() => addItem('employers', EMPTY_EMPLOYER)}>+ Add Employer</button>

              <div className="divider" />

              <SectionTitle>Properties</SectionTitle>
              {form.properties.map((prop, i) => (
                <div key={i} className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>Property #{i + 1}</span>
                    <button onClick={() => removeItem('properties', i)} style={{ background: 'none', border: 'none', color: '#F08080', cursor: 'pointer', fontSize: '0.85rem' }}>Remove</button>
                  </div>
                  <Field label="Description">
                    <input className="form-input" placeholder="e.g. 2BHK flat in Rohini, Delhi"
                      value={prop.description} onChange={e => updateItem('properties', i, 'description', e.target.value)} />
                  </Field>
                  <Field label="Location">
                    <input className="form-input" placeholder="e.g. Rohini, New Delhi"
                      value={prop.location} onChange={e => updateItem('properties', i, 'location', e.target.value)} />
                  </Field>
                </div>
              ))}
              <button className="btn-ghost" onClick={() => addItem('properties', EMPTY_PROPERTY)}>+ Add Property</button>
            </div>
          )}

          {/* ── Step 3: Family Contact ──── */}
          {step === 3 && (
            <div className="animate-fade-in">
              <SectionTitle>Family Members & Primary Contact</SectionTitle>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: 24 }}>
                Mark one person as the primary contact — their details will appear in all drafted letters.
              </p>
              {form.family_members.map((member, i) => (
                <div key={i} className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14, alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>Member #{i + 1}</span>
                      {member.is_primary_contact && (
                        <span style={{ fontSize: '0.7rem', background: 'rgba(201,168,76,0.15)', color: 'var(--gold)', padding: '2px 8px', borderRadius: 10, fontWeight: 600 }}>
                          PRIMARY CONTACT
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: 12 }}>
                      {!member.is_primary_contact && (
                        <button onClick={() => {
                          setForm(f => ({ ...f, family_members: f.family_members.map((m, idx) => ({ ...m, is_primary_contact: idx === i })) }))
                        }} style={{ background: 'none', border: 'none', color: 'var(--gold)', cursor: 'pointer', fontSize: '0.8rem' }}>
                          Set as Primary
                        </button>
                      )}
                      {form.family_members.length > 1 && (
                        <button onClick={() => removeItem('family_members', i)} style={{ background: 'none', border: 'none', color: '#F08080', cursor: 'pointer', fontSize: '0.85rem' }}>Remove</button>
                      )}
                    </div>
                  </div>
                  <Row>
                    <Field label="Full Name">
                      <input className="form-input" placeholder="Name of family member"
                        value={member.name} onChange={e => updateItem('family_members', i, 'name', e.target.value)} />
                    </Field>
                    <Field label="Relation to Deceased">
                      <select className="form-input" value={member.relation} onChange={e => updateItem('family_members', i, 'relation', e.target.value)}>
                        <option value="spouse">Spouse</option>
                        <option value="son">Son</option>
                        <option value="daughter">Daughter</option>
                        <option value="parent">Parent</option>
                        <option value="sibling">Sibling</option>
                        <option value="other">Other</option>
                      </select>
                    </Field>
                  </Row>
                  <Row>
                    <Field label="Phone">
                      <input className="form-input" placeholder="+91 98765 43210"
                        value={member.phone} onChange={e => updateItem('family_members', i, 'phone', e.target.value)} />
                    </Field>
                    <Field label="Email">
                      <input className="form-input" type="email" placeholder="email@example.com"
                        value={member.email} onChange={e => updateItem('family_members', i, 'email', e.target.value)} />
                    </Field>
                  </Row>
                </div>
              ))}
              <button className="btn-ghost" onClick={() => addItem('family_members', { ...EMPTY_MEMBER, is_primary_contact: false })}>
                + Add Family Member
              </button>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div style={{
            marginTop: 16, padding: '14px 18px',
            background: 'rgba(220,80,80,0.1)', border: '1px solid rgba(220,80,80,0.25)',
            borderRadius: 10, color: '#F08080', fontSize: '0.88rem',
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Nav Buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
          <button className="btn-secondary" onClick={() => setStep(s => s - 1)} disabled={step === 0}
            style={{ opacity: step === 0 ? 0.3 : 1, pointerEvents: step === 0 ? 'none' : 'auto' }}>
            ← Back
          </button>

          {step < STEPS.length - 1 ? (
            <button className="btn-primary" onClick={() => setStep(s => s + 1)} disabled={!canNext()}>
              Continue →
            </button>
          ) : (
            <button className="btn-primary" onClick={handleSubmit} disabled={loading}
              style={{ minWidth: 180, justifyContent: 'center' }}>
              🚀 Generate Task List
            </button>
          )}
        </div>

        {step === STEPS.length - 1 && (
          <p style={{ textAlign: 'right', marginTop: 8, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            This may take 30–60 seconds while the AI drafts all letters.
          </p>
        )}
        </div>
      </div>
    </>
  )
}

function SectionTitle({ children }) {
  return <h3 style={{
    fontFamily: "'Cormorant Garamond', serif",
    fontSize: '1.3rem', fontWeight: 600,
    margin: '0 0 20px', color: 'var(--text-primary)',
  }}>{children}</h3>
}

function Field({ label, children }) {
  return (
    <div style={{ flex: 1, minWidth: 0 }}>
      <label className="form-label">{label}</label>
      {children}
    </div>
  )
}

function Row({ children }) {
  return (
    <div style={{ display: 'flex', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
      {children}
    </div>
  )
}
