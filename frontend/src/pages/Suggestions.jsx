import { useEffect, useState } from 'react'
import { api } from '../api'

const TIER_LABEL = {
  ai_auto:           'AI 자동',
  ai_after_approval: 'AI (승인 후)',
  operator_manual:   '운영자 직접',
}
const TIER_BADGE = {
  ai_auto:           'badge-ai-auto',
  ai_after_approval: 'badge-ai-after',
  operator_manual:   'badge-operator-manual',
}

const PLATFORM = {
  product_analyzer: { label: '스마트스토어', color: '#03c75a', bg: '#e6f9ee' },
  ad_analyzer:      { label: '검색광고',     color: '#1a73e8', bg: '#e8f0fe' },
}

export default function Suggestions() {
  const [items, setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy]     = useState(null)
  const [tab, setTab]       = useState('product_analyzer')

  function load() {
    setLoading(true)
    api.getSuggestions()
      .then(setItems)
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function approve(id) {
    setBusy(id)
    try { await api.approveSuggestion(id); load() }
    catch (e) { alert(e.message) }
    finally { setBusy(null) }
  }

  async function reject(id) {
    setBusy(id)
    try { await api.rejectSuggestion(id); load() }
    catch (e) { alert(e.message) }
    finally { setBusy(null) }
  }

  const pending = items.filter(s => s.status === 'pending')
  const done    = items.filter(s => s.status !== 'pending')

  const PRIORITIES = ['high', 'medium', 'low']
  const PRIORITY_LABEL = { high: '높음', medium: '보통', low: '낮음' }

  const byAgent = agent => pending.filter(s => s.agent === agent)
  const byAgentAndPriority = (agent, priority) =>
    pending.filter(s => s.agent === agent && s.priority === priority)
  const doneByAgent = agent => done.filter(s => s.agent === agent)

  const tabs = [
    { key: 'product_analyzer', ...PLATFORM.product_analyzer },
    { key: 'ad_analyzer',      ...PLATFORM.ad_analyzer },
  ]

  return (
    <>
      <div className="page-title">제안함</div>

      {/* 탭 */}
      <div className="suggest-tabs">
        {tabs.map(t => {
          const count = byAgent(t.key).length
          return (
            <button
              key={t.key}
              className={`suggest-tab${tab === t.key ? ' active' : ''}`}
              style={tab === t.key ? { borderBottomColor: t.color, color: t.color } : {}}
              onClick={() => setTab(t.key)}
            >
              {t.label}
              {count > 0 && (
                <span
                  className="tab-count"
                  style={tab === t.key ? { background: t.color } : {}}
                >
                  {count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {loading && <div className="empty">불러오는 중…</div>}

      {/* 대기 제안 */}
      {!loading && byAgent(tab).length === 0 && (
        <div className="empty">대기 중인 제안이 없습니다.</div>
      )}

      {!loading && PRIORITIES.map(priority => {
        const group = byAgentAndPriority(tab, priority)
        if (group.length === 0) return null
        return (
          <div key={priority} className="priority-group">
            <div className={`priority-group-header priority-header-${priority}`}>
              <span className={`badge badge-${priority}`}>{PRIORITY_LABEL[priority]}</span>
              <span className="priority-group-count">{group.length}개</span>
            </div>
            {group.map(s => (
              <SuggestionCard
                key={s.suggestion_id}
                s={s}
                busy={busy}
                onApprove={approve}
                onReject={reject}
                platform={PLATFORM[s.agent]}
              />
            ))}
          </div>
        )
      })}

      {/* 처리 완료 */}
      {doneByAgent(tab).length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-title">처리 완료</div>
          <table className="table">
            <thead>
              <tr>
                <th>대상</th>
                <th>유형</th>
                <th>상태</th>
              </tr>
            </thead>
            <tbody>
              {doneByAgent(tab).map(s => (
                <tr key={s.suggestion_id}>
                  <td>{s.target_name}</td>
                  <td>{s.action_type}</td>
                  <td><span className={`badge badge-${s.status}`}>{s.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

function SuggestionCard({ s, busy, onApprove, onReject, platform }) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <span className={`badge badge-${s.priority}`}>{s.priority}</span>
            <span className={`badge ${TIER_BADGE[s.execution_tier]}`}>
              {TIER_LABEL[s.execution_tier]}
            </span>
            <strong style={{ fontSize: 13 }}>{s.action_type}</strong>
          </div>

          <div style={{ marginTop: 10, fontWeight: 600, fontSize: 14 }}>{s.target_name}</div>

          <div className="suggest-change">
            <span className="suggest-current">{s.current_value}</span>
            <span className="suggest-arrow">→</span>
            <span className="suggest-proposed">{s.proposed_value}</span>
          </div>

          <div className="text-muted mt-8">{s.reason}</div>
          <div className="text-muted mt-8">만료: {new Date(s.expires_at).toLocaleString('ko-KR')}</div>
        </div>

        <div style={{ marginLeft: 16, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <button
            className="btn btn-success"
            disabled={busy === s.suggestion_id}
            onClick={() => onApprove(s.suggestion_id)}
          >승인</button>
          <button
            className="btn btn-danger"
            disabled={busy === s.suggestion_id}
            onClick={() => onReject(s.suggestion_id)}
          >거절</button>
        </div>
      </div>
    </div>
  )
}
