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
  product_analyzer:  { label: '스마트스토어', color: '#03c75a', bg: '#e6f9ee' },
  ad_analyzer:       { label: '검색광고',     color: '#1a73e8', bg: '#e8f0fe' },
  coupang_analyzer:  { label: '쿠팡',         color: '#e4371c', bg: '#fdecea' },
}

const PRIORITIES = ['high', 'medium', 'low']
const PRIORITY_LABEL = { high: '높음', medium: '보통', low: '낮음' }

const REJECTION_TAGS = [
  { tag: '시즌맞지않음', label: '시즌 안 맞음' },
  { tag: '이미시도해봤음', label: '이미 해봤음' },
  { tag: '방향이다름',    label: '방향이 다름' },
  { tag: '여력없음',      label: '지금 여력 없음' },
  { tag: '기타',          label: '기타' },
]

const STATUS_LABEL = { approved: '승인', rejected: '거절', expired: '만료' }

export default function Suggestions() {
  const [items, setItems]     = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy]       = useState(null)
  const [tab, setTab]         = useState('pending')

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

  async function reject(id, rejectionTag) {
    setBusy(id)
    try { await api.rejectSuggestion(id, { rejection_tag: rejectionTag ?? null }); load() }
    catch (e) { alert(e.message) }
    finally { setBusy(null) }
  }

  const pendingItems   = items.filter(s => s.status === 'pending' && s.validator_verdict !== 'NEEDS_DATA')
  const needsDataItems = items.filter(s => s.status === 'pending' && s.validator_verdict === 'NEEDS_DATA')
  const doneItems      = items.filter(s => s.status !== 'pending')

  const tabs = [
    { key: 'pending',   label: '대기 제안',      count: pendingItems.length },
    { key: 'history',   label: '승인/거절 이력',  count: doneItems.length },
    { key: 'needsdata', label: '관찰 필요',       count: needsDataItems.length },
  ]

  return (
    <>
      <div className="page-title">제안함</div>

      <div className="suggest-tabs">
        {tabs.map(t => (
          <button
            key={t.key}
            className={`suggest-tab${tab === t.key ? ' active' : ''}`}
            style={tab === t.key ? { borderBottomColor: '#374151', color: '#374151' } : {}}
            onClick={() => setTab(t.key)}
          >
            {t.label}
            {t.count > 0 && (
              <span className="tab-count" style={tab === t.key ? { background: '#374151' } : {}}>
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {loading && <div className="empty">불러오는 중…</div>}

      {/* ── 대기 제안 탭 ── */}
      {!loading && tab === 'pending' && (
        pendingItems.length === 0
          ? <div className="empty">대기 중인 제안이 없습니다.</div>
          : <PendingList items={pendingItems} busy={busy} onApprove={approve} onReject={reject} />
      )}

      {/* ── 승인/거절 이력 탭 ── */}
      {!loading && tab === 'history' && (
        doneItems.length === 0
          ? <div className="empty">처리된 제안 이력이 없습니다.</div>
          : doneItems.map(s => <DoneCard key={s.suggestion_id} s={s} />)
      )}

      {/* ── 관찰 필요 탭 ── */}
      {!loading && tab === 'needsdata' && (
        needsDataItems.length === 0
          ? <div className="empty">관찰이 필요한 항목이 없습니다.</div>
          : <>
              <div className="card" style={{ background: '#fffbeb', border: '1px solid #fde68a', marginBottom: 16 }}>
                <p style={{ fontSize: 13, color: '#92400e', margin: 0 }}>
                  데이터가 부족하여 AI가 확신 있는 제안을 생성하지 못한 항목입니다.
                  수집 횟수가 늘어나거나 시즌이 바뀌면 재평가됩니다.
                </p>
              </div>
              {needsDataItems.map(s => (
                <NeedsDataCard key={s.suggestion_id} s={s} busy={busy} onApprove={approve} onReject={reject} />
              ))}
            </>
      )}
    </>
  )
}

/* ── 대기 제안 목록: 플랫폼별 + 우선순위별 그룹 ── */
function PendingList({ items, busy, onApprove, onReject }) {
  const agents = ['product_analyzer', 'ad_analyzer', 'coupang_analyzer']

  return (
    <>
      {agents.map(agent => {
        const agentItems = items.filter(s => s.agent === agent)
        if (agentItems.length === 0) return null
        const meta = PLATFORM[agent]
        const newItems    = agentItems.filter(s => !s.is_repeat)
        const repeatItems = agentItems.filter(s => s.is_repeat)

        return (
          <div key={agent}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8,
              margin: '20px 0 10px', paddingBottom: 6, borderBottom: '2px solid #f0f0f0',
            }}>
              <span style={{
                padding: '2px 10px', borderRadius: 12, fontSize: 12, fontWeight: 700,
                color: meta.color, background: meta.bg,
              }}>{meta.label}</span>
              <span className="text-muted" style={{ fontSize: 13 }}>{agentItems.length}개</span>
            </div>

            {newItems.length > 0 && (
              <>
                <div className="section-header">새 제안</div>
                {PRIORITIES.map(priority => {
                  const group = newItems.filter(s => s.priority === priority)
                  if (group.length === 0) return null
                  return (
                    <div key={priority} className="priority-group">
                      <div className={`priority-group-header priority-header-${priority}`}>
                        <span className={`badge badge-${priority}`}>{PRIORITY_LABEL[priority]}</span>
                        <span className="priority-group-count">{group.length}개</span>
                      </div>
                      {group.map(s => (
                        <SuggestionCard key={s.suggestion_id} s={s} busy={busy} onApprove={onApprove} onReject={onReject} platform={meta} />
                      ))}
                    </div>
                  )
                })}
              </>
            )}

            {repeatItems.length > 0 && (
              <>
                <div className="section-header" style={{ marginTop: 16 }}>
                  재제안
                  <span className="text-muted" style={{ fontSize: 12, fontWeight: 400, marginLeft: 8 }}>
                    이전에 거절/만료된 항목의 재시도
                  </span>
                </div>
                {PRIORITIES.map(priority => {
                  const group = repeatItems.filter(s => s.priority === priority)
                  if (group.length === 0) return null
                  return (
                    <div key={priority} className="priority-group">
                      <div className={`priority-group-header priority-header-${priority}`}>
                        <span className={`badge badge-${priority}`}>{PRIORITY_LABEL[priority]}</span>
                        <span className="priority-group-count">{group.length}개</span>
                      </div>
                      {group.map(s => (
                        <SuggestionCard key={s.suggestion_id} s={s} busy={busy} onApprove={onApprove} onReject={onReject} platform={meta} isRepeat />
                      ))}
                    </div>
                  )
                })}
              </>
            )}
          </div>
        )
      })}
    </>
  )
}

/* ── 제안 카드 ── */
function SuggestionCard({ s, busy, onApprove, onReject, platform, isRepeat }) {
  const [showTags, setShowTags] = useState(false)
  const isBusy = busy === s.suggestion_id

  return (
    <div className="card" style={isRepeat ? { borderLeft: '3px solid #f59e0b' } : {}}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <span className={`badge badge-${s.priority}`}>{s.priority}</span>
            <span className={`badge ${TIER_BADGE[s.execution_tier]}`}>
              {TIER_LABEL[s.execution_tier]}
            </span>
            {isRepeat && <span className="badge tier-operator">재제안</span>}
            {s.validator_verdict === 'WARN' && (
              <span style={{ fontSize: 11, color: '#92400e', background: '#fffbeb', padding: '1px 6px', borderRadius: 4 }}>주의</span>
            )}
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

        <div style={{ marginLeft: 16, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 8, minWidth: 80 }}>
          <button className="btn btn-success" disabled={isBusy || showTags} onClick={() => onApprove(s.suggestion_id)}>
            승인
          </button>
          {!showTags && (
            <button className="btn btn-danger" disabled={isBusy} onClick={() => setShowTags(true)}>
              거절
            </button>
          )}
          {showTags && (
            <button className="btn btn-ghost" style={{ fontSize: 11, color: '#999' }} onClick={() => setShowTags(false)}>
              취소
            </button>
          )}
        </div>
      </div>

      {showTags && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
          <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>거절 이유를 선택하세요</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {REJECTION_TAGS.map(({ tag, label }) => (
              <button
                key={tag}
                onClick={() => { setShowTags(false); onReject(s.suggestion_id, tag) }}
                disabled={isBusy}
                style={{ padding: '5px 12px', borderRadius: 20, border: '1px solid #ddd', background: '#f7f7f7', fontSize: 12, cursor: 'pointer', color: '#444' }}
              >{label}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/* ── 관찰 필요 카드 (승인/거절 가능하지만 안내 포함) ── */
function NeedsDataCard({ s, busy, onApprove, onReject }) {
  const meta = PLATFORM[s.agent] ?? { label: s.agent, color: '#6b7280', bg: '#f3f4f6' }
  const [showTags, setShowTags] = useState(false)
  const isBusy = busy === s.suggestion_id

  return (
    <div className="card" style={{ borderLeft: '3px solid #d1d5db' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', marginBottom: 6 }}>
            <span style={{ padding: '2px 8px', borderRadius: 12, fontSize: 12, fontWeight: 700, color: meta.color, background: meta.bg }}>
              {meta.label}
            </span>
            <span className={`badge badge-${s.priority}`}>{s.priority}</span>
            <strong style={{ fontSize: 13 }}>{s.action_type}</strong>
          </div>

          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 6 }}>{s.target_name}</div>

          <div className="suggest-change">
            <span className="suggest-current">{s.current_value}</span>
            <span className="suggest-arrow">→</span>
            <span className="suggest-proposed">{s.proposed_value}</span>
          </div>

          <div className="text-muted mt-8">{s.reason}</div>
          <div style={{ marginTop: 8, fontSize: 12, color: '#6b7280', background: '#f9fafb', padding: '6px 10px', borderRadius: 4 }}>
            데이터 부족 — 분석을 더 실행하거나 시즌 변화 후 재평가됩니다
          </div>
        </div>

        <div style={{ marginLeft: 16, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 8, minWidth: 80 }}>
          <button className="btn btn-success" disabled={isBusy || showTags} onClick={() => onApprove(s.suggestion_id)}>
            승인
          </button>
          {!showTags && (
            <button className="btn btn-danger" disabled={isBusy} onClick={() => setShowTags(true)}>
              거절
            </button>
          )}
          {showTags && (
            <button className="btn btn-ghost" style={{ fontSize: 11, color: '#999' }} onClick={() => setShowTags(false)}>
              취소
            </button>
          )}
        </div>
      </div>

      {showTags && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
          <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>거절 이유를 선택하세요</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {REJECTION_TAGS.map(({ tag, label }) => (
              <button
                key={tag}
                onClick={() => { setShowTags(false); onReject(s.suggestion_id, tag) }}
                disabled={isBusy}
                style={{ padding: '5px 12px', borderRadius: 20, border: '1px solid #ddd', background: '#f7f7f7', fontSize: 12, cursor: 'pointer', color: '#444' }}
              >{label}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/* ── 처리 완료 카드 ── */
function DoneCard({ s }) {
  const meta = PLATFORM[s.agent] ?? { label: s.agent, color: '#6b7280', bg: '#f3f4f6' }
  return (
    <div className="card" style={{ padding: '12px 16px', marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', marginBottom: 6 }}>
            <span style={{ padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 700, color: meta.color, background: meta.bg }}>
              {meta.label}
            </span>
            <span className={`badge badge-${s.status}`}>{STATUS_LABEL[s.status] ?? s.status}</span>
            <span className={`badge badge-${s.priority}`}>{s.priority}</span>
            <strong style={{ fontSize: 13 }}>{s.action_type}</strong>
            <span style={{ fontSize: 13, color: '#555' }}>{s.target_name}</span>
          </div>
          <div className="suggest-change" style={{ marginBottom: 4 }}>
            <span className="suggest-current">{s.current_value}</span>
            <span className="suggest-arrow">→</span>
            <span className="suggest-proposed">{s.proposed_value}</span>
          </div>
          <div className="text-muted" style={{ fontSize: 12 }}>{s.reason}</div>
          {s.status === 'rejected' && s.rejection_tag && (
            <div style={{ marginTop: 4 }}>
              <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 12, background: '#f0f0f0', fontSize: 11, color: '#666' }}>
                {s.rejection_tag}
              </span>
            </div>
          )}
        </div>
        <div className="text-muted" style={{ fontSize: 11, marginLeft: 12, whiteSpace: 'nowrap', flexShrink: 0 }}>
          {new Date(s.created_at).toLocaleDateString('ko-KR')}
        </div>
      </div>
    </div>
  )
}
