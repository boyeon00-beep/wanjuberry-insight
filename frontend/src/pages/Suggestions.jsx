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
  product_analyzer:  { key: 'smartstore', label: '스마트스토어', color: '#03c75a', bg: '#e6f9ee' },
  ad_analyzer:       { key: 'ad',         label: '검색광고',     color: '#1a73e8', bg: '#e8f0fe' },
  coupang_analyzer:  { key: 'coupang',    label: '쿠팡',         color: '#e4371c', bg: '#fdecea' },
}

const AGENT_BY_TAB = {
  smartstore: 'product_analyzer',
  ad:         'ad_analyzer',
  coupang:    'coupang_analyzer',
}

const PRIORITIES = ['high', 'medium', 'low']
const PRIORITY_LABEL = { high: '높음', medium: '보통', low: '낮음' }

function groupByProduct(items) {
  const map = {}
  items.forEach(s => {
    const key = s.target_id || s.target_name
    if (!map[key]) map[key] = { name: s.target_name, items: [] }
    map[key].items.push(s)
  })
  // 각 상품 내부는 priority 순 정렬
  return Object.values(map).map(g => ({
    ...g,
    items: [...g.items].sort((a, b) => PRIORITIES.indexOf(a.priority) - PRIORITIES.indexOf(b.priority)),
  }))
}

const REJECTION_TAGS = [
  { tag: '시즌맞지않음', label: '시즌 안 맞음' },
  { tag: '이미시도해봤음', label: '이미 해봤음' },
  { tag: '방향이다름',    label: '방향이 다름' },
  { tag: '여력없음',      label: '지금 여력 없음' },
  { tag: '기타',          label: '기타' },
]

const STATUS_LABEL = { approved: '승인', rejected: '거절', expired: '만료' }

export default function Suggestions() {
  const [items, setItems]               = useState([])
  const [loading, setLoading]           = useState(true)
  const [busy, setBusy]                 = useState(null)
  const [tab, setTab]                   = useState('smartstore')
  const [aiExecutionEnabled, setAiExec] = useState(true)

  function load() {
    setLoading(true)
    api.getSuggestions()
      .then(setItems)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    api.getConfig().then(r => setAiExec(r.ai_execution_enabled ?? true)).catch(() => {})
  }, [])

  async function approve(id) {
    setBusy(id)
    try { await api.approveSuggestion(id) }
    catch (e) { alert(e.message) }
    finally { setBusy(null); load() }
  }

  async function reject(id, rejectionTag) {
    setBusy(id)
    try { await api.rejectSuggestion(id, { rejection_tag: rejectionTag ?? null }); load() }
    catch (e) { alert(e.message) }
    finally { setBusy(null) }
  }

  const pendingCount = (agentKey) =>
    items.filter(s => s.status === 'pending' && s.agent === agentKey).length

  const doneItems = items.filter(s => s.status !== 'pending')

  const platformTabs = [
    { key: 'smartstore', label: '스마트스토어', agent: 'product_analyzer', color: '#03c75a' },
    { key: 'ad',         label: '검색광고',     agent: 'ad_analyzer',      color: '#1a73e8' },
    { key: 'coupang',    label: '쿠팡',         agent: 'coupang_analyzer', color: '#e4371c' },
  ]

  return (
    <>
      <div className="page-title">제안함</div>

      <div className="suggest-tabs">
        {platformTabs.map(t => {
          const cnt = pendingCount(t.agent)
          const isActive = tab === t.key
          return (
            <button
              key={t.key}
              className={`suggest-tab${isActive ? ' active' : ''}`}
              style={isActive ? { borderBottomColor: t.color, color: t.color } : {}}
              onClick={() => setTab(t.key)}
            >
              {t.label}
              {cnt > 0 && (
                <span className="tab-count" style={isActive ? { background: t.color } : {}}>
                  {cnt}
                </span>
              )}
            </button>
          )
        })}
        <button
          className={`suggest-tab${tab === 'history' ? ' active' : ''}`}
          style={tab === 'history' ? { borderBottomColor: '#374151', color: '#374151' } : {}}
          onClick={() => setTab('history')}
        >
          이력
          {doneItems.length > 0 && (
            <span className="tab-count" style={tab === 'history' ? { background: '#374151' } : {}}>
              {doneItems.length}
            </span>
          )}
        </button>
      </div>

      {loading && <div className="empty">불러오는 중…</div>}

      {/* ── 플랫폼 탭 ── */}
      {!loading && tab !== 'history' && (() => {
        const agentKey = AGENT_BY_TAB[tab]
        const meta     = PLATFORM[agentKey]
        const all      = items.filter(s => s.status === 'pending' && s.agent === agentKey)
        const newItems     = all.filter(s => !s.is_repeat && s.validator_verdict !== 'NEEDS_DATA')
        const repeatItems  = all.filter(s =>  s.is_repeat && s.validator_verdict !== 'NEEDS_DATA')
        const needsData    = all.filter(s => s.validator_verdict === 'NEEDS_DATA')

        if (all.length === 0) {
          return <div className="empty">대기 중인 {meta.label} 제안이 없습니다.</div>
        }

        return (
          <>
            {tab === 'coupang' && (
              <div style={{ background: '#fff8e1', border: '1px solid #ffe082', borderRadius: 8, padding: '10px 14px', marginBottom: 16, fontSize: 13, color: '#5d4037', lineHeight: 1.7 }}>
                <strong>⚠ 쿠팡 승인 순서 주의</strong><br />
                <strong>상품명_수정 · 태그_추가 · 태그_수정</strong>은 같은 상품에 동시에 승인하면 앞의 변경이 취소될 수 있습니다.<br />
                실행 로그에서 <strong>[수정 확인]</strong>으로 쿠팡 반영을 확인한 뒤 다음 제안을 승인하세요.<br />
                <span style={{ color: '#7e7e7e' }}>가격_검토 · 재입고_제안은 별도 API라 동시 승인 무관합니다.</span>
              </div>
            )}

            {newItems.length > 0 && (
              <section>
                <div className="section-header">새 제안</div>
                {groupByProduct(newItems).map(group => (
                  <div key={group.name} className="product-group">
                    <div className="product-group-header">{group.name}</div>
                    {group.items.map(s => (
                      <SuggestionCard key={s.suggestion_id} s={s} busy={busy} onApprove={approve} onReject={reject} platform={meta} aiExecutionEnabled={aiExecutionEnabled} />
                    ))}
                  </div>
                ))}
              </section>
            )}

            {repeatItems.length > 0 && (
              <section style={{ marginTop: newItems.length > 0 ? 20 : 0 }}>
                <div className="section-header">
                  재제안
                  <span className="text-muted" style={{ fontSize: 12, fontWeight: 400, marginLeft: 8 }}>
                    이전에 거절/만료된 항목의 재시도
                  </span>
                </div>
                {groupByProduct(repeatItems).map(group => (
                  <div key={group.name} className="product-group">
                    <div className="product-group-header">{group.name}</div>
                    {group.items.map(s => (
                      <SuggestionCard key={s.suggestion_id} s={s} busy={busy} onApprove={approve} onReject={reject} platform={meta} isRepeat aiExecutionEnabled={aiExecutionEnabled} />
                    ))}
                  </div>
                ))}
              </section>
            )}

            {needsData.length > 0 && (
              <section style={{ marginTop: (newItems.length + repeatItems.length) > 0 ? 20 : 0 }}>
                <div className="section-header">관찰 필요</div>
                <div className="card" style={{ background: '#fffbeb', border: '1px solid #fde68a', marginBottom: 12 }}>
                  <p style={{ fontSize: 13, color: '#92400e', margin: 0 }}>
                    데이터가 부족하여 AI가 확신 있는 제안을 생성하지 못한 항목입니다.
                    수집 횟수가 늘어나거나 시즌이 바뀌면 재평가됩니다.
                  </p>
                </div>
                {needsData.map(s => (
                  <SuggestionCard key={s.suggestion_id} s={s} busy={busy} onApprove={approve} onReject={reject} platform={meta} isNeedsData aiExecutionEnabled={aiExecutionEnabled} />
                ))}
              </section>
            )}
          </>
        )
      })()}

      {/* ── 이력 탭 ── */}
      {!loading && tab === 'history' && (
        doneItems.length === 0
          ? <div className="empty">처리된 제안 이력이 없습니다.</div>
          : doneItems.map(s => <DoneCard key={s.suggestion_id} s={s} />)
      )}
    </>
  )
}

/* ── 제안 카드 ── */
function SuggestionCard({ s, busy, onApprove, onReject, platform, isRepeat, isNeedsData, aiExecutionEnabled = true }) {
  const [showTags, setShowTags] = useState(false)
  const isBusy = busy === s.suggestion_id

  const borderStyle = isNeedsData
    ? { borderLeft: '3px solid #d1d5db' }
    : isRepeat
      ? { borderLeft: '3px solid #f59e0b' }
      : {}

  return (
    <div className="card" style={borderStyle}>
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

          {isNeedsData && (
            <div style={{ marginTop: 8, fontSize: 12, color: '#6b7280', background: '#f9fafb', padding: '6px 10px', borderRadius: 4 }}>
              데이터 부족 — 분석을 더 실행하거나 시즌 변화 후 재평가됩니다
            </div>
          )}

          {(s.execution_tier === 'operator_manual' || (!aiExecutionEnabled && s.execution_tier === 'ai_auto')) && (
            <div style={{ marginTop: 8, fontSize: 12, color: '#6b7280', background: '#f0f4ff', padding: '6px 10px', borderRadius: 4, border: '1px solid #c7d2fe' }}>
              운영자 직접 실행 항목 — 아래 버튼은 직접 완료했음을 기록합니다
            </div>
          )}

          <div className="text-muted mt-8">만료: {new Date(s.expires_at).toLocaleString('ko-KR')}</div>
        </div>

        <div style={{ marginLeft: 16, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 8, minWidth: 80 }}>
          <button className="btn btn-success" disabled={isBusy || showTags} onClick={() => onApprove(s.suggestion_id)}>
            {(s.execution_tier === 'operator_manual' || (!aiExecutionEnabled && s.execution_tier === 'ai_auto')) ? '직접 완료' : '승인'}
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
