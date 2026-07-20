import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCase, getTaskDraft, approveTask, sendGmailTask, editDraft, rejectTask, completeTask, triggerFollowup, getCaseTasks } from '../api'
import StatusBadge from '../components/StatusBadge'
import { INSTITUTION_ICONS, INSTITUTION_COLORS, formatDate } from '../utils'

export default function Review() {
  const { caseId, taskId } = useParams()
  const navigate = useNavigate()

  const [caseData, setCaseData] = useState(null)
  const [task, setTask] = useState(null)
  const [draft, setDraft] = useState(null)
  const [allTasks, setAllTasks] = useState([])
  const [editMode, setEditMode] = useState(false)
  const [editedBody, setEditedBody] = useState('')
  const [editedSubject, setEditedSubject] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(null)
  const [toast, setToast] = useState(null)
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [recipientEmail, setRecipientEmail] = useState('')

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const load = async () => {
    try {
      const [cRes, tRes, dRes] = await Promise.all([
        getCase(caseId),
        getCaseTasks(caseId),
        getTaskDraft(taskId),
      ])
      setCaseData(cRes.data)
      const tasks = tRes.data
      setAllTasks(tasks)
      const thisTask = tasks.find(t => t.id === taskId)
      setTask(thisTask)
      setDraft(dRes.data)
      setEditedBody(dRes.data.body)
      setEditedSubject(dRes.data.subject || '')
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [taskId])

  const handleApprove = async () => {
    setActionLoading('approve')
    try {
      await approveTask(taskId)
      showToast('✅ Draft approved and marked as Sent')
      await load()
    } catch (e) {
      showToast(e.response?.data?.detail || 'Failed to approve', 'error')
    } finally { setActionLoading(null) }
  }

  const handleSendGmailSubmit = async (e) => {
    e.preventDefault()
    if (!recipientEmail) return
    setActionLoading('send_gmail')
    try {
      const res = await sendGmailTask(taskId, recipientEmail)
      showToast(`🌐 Sent via Gmail API to ${recipientEmail}!`)
      setShowEmailModal(false)
      await load()
    } catch (e) {
      showToast(e.response?.data?.detail || 'Gmail sending failed. Make sure you are signed in with Google.', 'error')
    } finally { setActionLoading(null) }
  }

  const handleSendEmailSubmit = async (e) => {
    e.preventDefault()
    if (!recipientEmail) return
    setActionLoading('send_email')
    try {
      const res = await sendTaskEmail(taskId, recipientEmail)
      showToast(`✉️ ${res.data.result.message}`)
      setShowEmailModal(false)
      await load()
    } catch (e) {
      showToast(e.response?.data?.detail || 'Failed to send email', 'error')
    } finally { setActionLoading(null) }
  }

  const handleSaveEdit = async () => {
    setActionLoading('save')
    try {
      const res = await editDraft(taskId, { subject: editedSubject, body: editedBody })
      setDraft(res.data)
      setEditMode(false)
      showToast('✏️ Draft updated')
    } catch (e) {
      showToast('Failed to save edits', 'error')
    } finally { setActionLoading(null) }
  }

  const handleReject = async () => {
    setActionLoading('reject')
    try {
      await rejectTask(taskId)
      showToast('Draft marked for revision', 'error')
      await load()
    } catch (e) {
      showToast('Failed to reject', 'error')
    } finally { setActionLoading(null) }
  }

  const handleComplete = async () => {
    setActionLoading('complete')
    try {
      await completeTask(taskId)
      showToast('✅ Task marked as Completed!')
      await load()
    } catch (e) {
      showToast('Failed to mark complete', 'error')
    } finally { setActionLoading(null) }
  }

  const handleFollowup = async () => {
    setActionLoading('followup')
    try {
      await triggerFollowup(taskId)
      showToast('Follow-up draft generated — review it above.')
      await load()
    } catch (e) {
      showToast(e.response?.data?.detail || 'Failed to generate follow-up', 'error')
    } finally { setActionLoading(null) }
  }

  // Navigate between tasks
  const currentIdx = allTasks.findIndex(t => t.id === taskId)
  const prevTask = allTasks[currentIdx - 1]
  const nextTask = allTasks[currentIdx + 1]

  if (loading) return (
    <div style={{ padding: '80px 24px', textAlign: 'center' }}>
      <div className="animate-pulse-soft" style={{ color: 'var(--text-muted)' }}>Loading draft…</div>
    </div>
  )

  if (!task || !draft) return (
    <div style={{ padding: '80px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
      Task or draft not found.
      <br/>
      <button className="btn-secondary" onClick={() => navigate(`/cases/${caseId}`)} style={{ marginTop: 16 }}>
        Back to Dashboard
      </button>
    </div>
  )

  const icon = INSTITUTION_ICONS[task.institution_type] || '📋'
  const color = INSTITUTION_COLORS[task.institution_type] || '#888'
  const attachments = draft.attachments ? JSON.parse(draft.attachments) : []

  return (
    <div style={{ minHeight: '100vh', padding: '40px 24px' }}>
      <div style={{ maxWidth: 860, margin: '0 auto' }}>

        {/* Toast */}
        {toast && (
          <div style={{
            position: 'fixed', top: 80, right: 24, zIndex: 999,
            padding: '12px 20px', borderRadius: 10,
            background: toast.type === 'error' ? 'rgba(220,80,80,0.2)' : 'rgba(92,138,110,0.2)',
            border: `1px solid ${toast.type === 'error' ? 'rgba(220,80,80,0.4)' : 'rgba(92,138,110,0.4)'}`,
            color: toast.type === 'error' ? '#F08080' : '#A8E4BC',
            fontSize: '0.88rem', fontWeight: 500,
            animation: 'fadeInUp 0.3s ease',
            backdropFilter: 'blur(12px)',
          }}>
            {toast.msg}
          </div>
        )}

        {/* Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 28, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          <button onClick={() => navigate('/cases')} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 0 }}>Cases</button>
          <span>/</span>
          <button onClick={() => navigate(`/cases/${caseId}`)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 0 }}>
            {caseData?.deceased_name}
          </button>
          <span>/</span>
          <span style={{ color: 'var(--text-primary)' }}>{task.task_type}</span>
        </div>

        {/* Task Header */}
        <div className="glass-card" style={{ padding: '24px 28px', marginBottom: 24, borderLeft: `4px solid ${color}` }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
              <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: `${color}20`, display: 'flex', alignItems: 'center',
                justifyContent: 'center', fontSize: '1.5rem', flexShrink: 0,
              }}>{icon}</div>
              <div>
                <h1 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '1.6rem', margin: '0 0 6px' }}>
                  {task.task_type}
                </h1>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{task.institution_name}</div>
              </div>
            </div>
            <StatusBadge status={task.status} />
          </div>

          {/* Attachments */}
          {attachments.length > 0 && (
            <div style={{ marginTop: 20 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
                Required Documents
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {attachments.map((doc, i) => (
                  <span key={i} style={{
                    padding: '4px 10px', borderRadius: 6,
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid var(--glass-border)',
                    fontSize: '0.77rem', color: 'var(--text-muted)',
                  }}>
                    📎 {doc}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Draft */}
        <div className="glass-card-solid" style={{ padding: '28px 32px', marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h2 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '1.3rem', margin: 0 }}>
              {draft.version > 1 ? `Follow-up Draft (v${draft.version})` : 'AI-Generated Draft'}
            </h2>
            {!editMode && task.status !== 'completed' && (
              <button className="btn-ghost" onClick={() => setEditMode(true)}>✏️ Edit</button>
            )}
          </div>

          {/* Subject */}
          <div style={{ marginBottom: 16 }}>
            <div className="form-label">Subject</div>
            {editMode ? (
              <input className="form-input" value={editedSubject}
                onChange={e => setEditedSubject(e.target.value)} />
            ) : (
              <div style={{
                padding: '10px 14px', background: 'rgba(255,255,255,0.04)',
                borderRadius: 8, fontSize: '0.9rem', color: 'var(--text-primary)',
                border: '1px solid var(--glass-border)',
              }}>
                {draft.subject || '—'}
              </div>
            )}
          </div>

          {/* Body */}
          <div>
            <div className="form-label">Letter Body</div>
            {editMode ? (
              <textarea className="form-textarea" rows={18} value={editedBody}
                onChange={e => setEditedBody(e.target.value)} />
            ) : (
              <div style={{
                padding: '16px 18px',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--glass-border)',
                borderRadius: 10,
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                lineHeight: 1.8,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-wrap',
                maxHeight: 500,
                overflowY: 'auto',
              }}>
                {draft.body}
              </div>
            )}
          </div>

          {/* Edit actions */}
          {editMode && (
            <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
              <button className="btn-success" onClick={handleSaveEdit} disabled={actionLoading === 'save'}>
                {actionLoading === 'save' ? '⏳ Saving…' : '💾 Save Changes'}
              </button>
              <button className="btn-ghost" onClick={() => { setEditMode(false); setEditedBody(draft.body); setEditedSubject(draft.subject || '') }}>
                Cancel
              </button>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        {!editMode && (
          <div className="glass-card" style={{ padding: '20px 24px' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Actions
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>

              {(task.status === 'awaiting_approval' || task.status === 'not_started') && (
                <>
                  <button className="btn-primary" onClick={() => {
                    setRecipientEmail(task.recipient_email || '')
                    setShowEmailModal(true)
                  }} disabled={!!actionLoading}>
                    ✉️ Send Direct Email
                  </button>
                  <button className="btn-success" onClick={handleApprove} disabled={!!actionLoading}>
                    {actionLoading === 'approve' ? '⏳ Approving…' : '✅ Approve & Mark Sent'}
                  </button>
                  <button className="btn-danger" onClick={handleReject} disabled={!!actionLoading}>
                    ❌ Reject
                  </button>
                </>
              )}

              {/* Email Send Modal */}
              {showEmailModal && (
                <div style={{
                  width: '100%', marginTop: 16, padding: '20px 24px',
                  background: 'rgba(201,168,76,0.06)', border: '1px solid rgba(201,168,76,0.3)',
                  borderRadius: 12, animation: 'fadeIn 0.2s ease',
                }}>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: 6, color: 'var(--gold)' }}>
                    ✉️ Send Letter via Gmail API
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 16 }}>
                    Automatically auto-detected recipient authority email for {task.institution_name}. Dispatches directly from your personal Gmail account.
                  </p>
                  <form onSubmit={handleSendGmailSubmit} style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, minWidth: 260 }}>
                      <input className="form-input" type="email" placeholder="e.g. claims@sbi.co.in or hr@company.com" required
                        value={recipientEmail} onChange={e => setRecipientEmail(e.target.value)} />
                    </div>
                    <button className="btn-primary" type="submit" disabled={actionLoading === 'send_gmail'}>
                      {actionLoading === 'send_gmail' ? '⏳ Sending via Gmail…' : '🌐 Send via My Gmail'}
                    </button>
                    <button className="btn-ghost" type="button" onClick={() => setShowEmailModal(false)}>
                      Cancel
                    </button>
                  </form>
                </div>
              )}

              {task.status === 'sent' && (
                <>
                  <button className="btn-success" onClick={handleComplete} disabled={!!actionLoading}>
                    {actionLoading === 'complete' ? '⏳…' : '🎉 Mark as Completed'}
                  </button>
                  <button className="btn-ghost" onClick={handleFollowup} disabled={!!actionLoading}>
                    {actionLoading === 'followup' ? '⏳ Generating…' : '🔔 Generate Follow-up'}
                  </button>
                </>
              )}

              {task.status === 'completed' && (
                <div style={{ color: '#A8E4BC', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                  ✅ This task has been resolved.
                </div>
              )}
            </div>
          </div>
        )}

        {/* Task Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 28 }}>
          <button
            className="btn-secondary"
            onClick={() => navigate(`/cases/${caseId}/tasks/${prevTask.id}`)}
            disabled={!prevTask}
            style={{ opacity: prevTask ? 1 : 0.3, pointerEvents: prevTask ? 'auto' : 'none' }}
          >
            ← Previous Task
          </button>
          <button className="btn-ghost" onClick={() => navigate(`/cases/${caseId}`)}>
            Back to Dashboard
          </button>
          <button
            className="btn-secondary"
            onClick={() => navigate(`/cases/${caseId}/tasks/${nextTask.id}`)}
            disabled={!nextTask}
            style={{ opacity: nextTask ? 1 : 0.3, pointerEvents: nextTask ? 'auto' : 'none' }}
          >
            Next Task →
          </button>
        </div>
      </div>
    </div>
  )
}
