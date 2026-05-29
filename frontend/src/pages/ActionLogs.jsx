import { useEffect, useState } from 'react'
import { api } from '../api'

const TIER_LABEL = {
  ai_auto:           'AI 자동',
  ai_after_approval: 'AI (승인 후)',
  operator_manual:   '운영자 직접',
}

const VERIFY_META = {
  matched:           { label: '반영됨',        cls: 'verdict-positive',     icon: '✅' },
  not_matched:       { label: '아직 미반영',    cls: 'verdict-pending',      icon: '⏳' },
  coupang_reviewing: { label: '쿠팡 검토 중',   cls: 'verdict-unmeasurable', icon: '🔍' },
  error:             { label: '확인 불가',       cls: 'verdict-negative',     icon: '❌' },
}

const STATUS_LABEL = {
  success:  '승인·실행',
  skipped:  '승인 (직접실행)',
  rejected: '거절',
  failed:   '실패',
}

const VERDICT_META = {
  positive:     { label: '효과 있음',  cls: 'verdict-positive' },
  neutral:      { label: '변화 없음',  cls: 'verdict-neutral' },
  negative:     { label: '역효과',     cls: 'verdict-negative' },
  unmeasurable: { label: '측정 불가',  cls: 'verdict-unmeasurable' },
  pending:      { label: '측정 대기',  cls: 'verdict-pending' },
}

const AGENT_LABEL = {
  product_analyzer: '스마트스토어',
  ad_analyzer:      '검색광고',
  coupang_analyzer: '쿠팡',
}

const MODE_COLOR = {
  PREPARE: '#075985',
  TEST:    '#854d0e',
  SCALE:   '#166534',
  DEFEND:  '#991b1b',
  LEARN:   '#5b21b6',
  REVIEW:  '#374151',
}

export default function ActionLogs() {
  const [logs, setLogs]               = useState([])
  const [loading, setLoading]         = useState(true)
  const [tab, setTab]                 = useState('logs')
  const [agentFilter, setAgentFilter] = useState('all')
  const [verifying, setVerifying]     = useState({})  // log_id → true

  useEffect(() => {
    api.getActionLogs()
      .then(data => setLogs([...data].reverse()))
      .finally(() => setLoading(false))
  }, [])

  const handleVerify = async (log_id) => {
    setVerifying(v => ({ ...v, [log_id]: true }))
    try {
      const res = await api.verifyActionLog(log_id)
      setLogs(prev => prev.map(l =>
        l.log_id === log_id
          ? { ...l, verify_status: res.verify_status, verified_at: new Date().toISOString() }
          : l
      ))
    } catch {
      // 실패 시 상태 유지
    } finally {
      setVerifying(v => ({ ...v, [log_id]: false }))
    }
  }

  const filteredLogs = agentFilter === 'all' ? logs : logs.filter(l => l.agent === agentFilter)

  const measured = logs.filter(l => l.effect_verdict && l.effect_verdict !== 'pending')
  const pending  = logs.filter(l => l.effect_verdict === 'pending')
  const filteredMeasured = agentFilter === 'all' ? measured : measured.filter(l => l.agent === agentFilter)

  const verdictCounts = measured.reduce((acc, l) => {
    acc[l.effect_verdict] = (acc[l.effect_verdict] ?? 0) + 1
    return acc
  }, {})

  const tabs = [
    { key: 'logs',    label: '실행 이력',  count: logs.length },
    { key: 'effects', label: '성과 측정',  count: measured.length },
  ]

  return (
    <>
      <div className="page-title">실행 로그</div>

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
              <span className="tab-count" style={tab === t.key ? { background: '#374151' } : {}}>{t.count}</span>
            )}
          </button>
        ))}
      </div>

      {loading && <div className="empty">불러오는 중…</div>}

      {!loading && (
        <>
          {/* 에이전트 필터 (공통) */}
          <div className="agent-filters">
            {['all', 'product_analyzer', 'ad_analyzer', 'coupang_analyzer'].map(a => (
              <button
                key={a}
                className={`agent-filter-btn${agentFilter === a ? ' active' : ''}`}
                onClick={() => setAgentFilter(a)}
              >
                {a === 'all' ? `전체 (${logs.length})` : `${AGENT_LABEL[a]} (${logs.filter(l => l.agent === a).length})`}
              </button>
            ))}
          </div>

          {/* ── 실행 이력 탭 ── */}
          {tab === 'logs' && (
            filteredLogs.length === 0
              ? <div className="empty">실행 이력이 없습니다.</div>
              : <div className="card">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>실행 시각</th>
                        <th>에이전트</th>
                        <th>대상</th>
                        <th>액션</th>
                        <th>전략 모드</th>
                        <th>실행 방식</th>
                        <th>결과</th>
                        <th>반영 확인</th>
                        <th>효과 측정</th>
                        <th>상세</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredLogs.map(log => {
                        const vm = log.effect_verdict ? VERDICT_META[log.effect_verdict] : null
                        const modeColor = MODE_COLOR[log.ad_strategy_mode] ?? '#6b7280'
                        const isVerifiable = log.execution_tier === 'ai_auto' && log.status === 'success'
                        const vStatus = log.verify_status
                        const vMeta = vStatus ? VERIFY_META[vStatus] : null
                        const isVerifying = verifying[log.log_id]
                        const canRetry = vStatus && vStatus !== 'matched'

                        return (
                          <tr key={log.log_id}>
                            <td className="text-muted" style={{ whiteSpace: 'nowrap' }}>
                              {new Date(log.executed_at).toLocaleString('ko-KR')}
                            </td>
                            <td className="text-muted">{AGENT_LABEL[log.agent] ?? log.agent ?? '-'}</td>
                            <td style={{ fontWeight: 500 }}>{log.target_name}</td>
                            <td>{log.action_type}</td>
                            <td>
                              {log.ad_strategy_mode
                                ? <span style={{ fontSize: 12, fontWeight: 700, color: modeColor }}>{log.ad_strategy_mode}</span>
                                : <span className="text-muted">-</span>}
                            </td>
                            <td>{TIER_LABEL[log.execution_tier] ?? log.execution_tier}</td>
                            <td>
                              <span className={`badge badge-${log.status}`}>
                                {STATUS_LABEL[log.status] ?? log.status}
                              </span>
                            </td>
                            <td style={{ whiteSpace: 'nowrap' }}>
                              {!isVerifiable ? (
                                <span className="text-muted">-</span>
                              ) : vMeta ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                  <span className={`badge ${vMeta.cls}`} style={{ fontSize: 11 }}>
                                    {vMeta.icon} {vMeta.label}
                                  </span>
                                  {log.verified_at && (
                                    <span className="text-muted" style={{ fontSize: 10 }}>
                                      {new Date(log.verified_at).toLocaleString('ko-KR', { month:'numeric', day:'numeric', hour:'2-digit', minute:'2-digit' })}
                                    </span>
                                  )}
                                  {canRetry && (
                                    <button
                                      onClick={() => handleVerify(log.log_id)}
                                      disabled={isVerifying}
                                      style={{ fontSize: 10, color: '#6b7280', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                                    >
                                      {isVerifying ? '확인 중…' : '다시확인'}
                                    </button>
                                  )}
                                </div>
                              ) : (
                                <button
                                  onClick={() => handleVerify(log.log_id)}
                                  disabled={isVerifying}
                                  style={{
                                    fontSize: 11, padding: '2px 8px',
                                    background: '#f3f4f6', border: '1px solid #d1d5db',
                                    borderRadius: 4, cursor: 'pointer', color: '#374151',
                                  }}
                                >
                                  {isVerifying ? '확인 중…' : '수정 확인'}
                                </button>
                              )}
                            </td>
                            <td>
                              {vm
                                ? <span className={`badge ${vm.cls}`}>{vm.label}</span>
                                : <span className="text-muted">-</span>}
                            </td>
                            <td className="text-muted" style={{ maxWidth: 260, wordBreak: 'break-all', fontSize: 12 }}>
                              {log.detail}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
          )}

          {/* ── 성과 측정 탭 ── */}
          {tab === 'effects' && (
            <>
              <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
                {['positive', 'neutral', 'negative', 'unmeasurable'].map(v => (
                  <div className="kpi-card" key={v}>
                    <div className="kpi-label">{VERDICT_META[v].label}</div>
                    <div className="kpi-value">
                      {verdictCounts[v] ?? 0}
                      <span style={{ fontSize: 14, color: '#9ca3af', marginLeft: 2 }}>건</span>
                    </div>
                  </div>
                ))}
                <div className="kpi-card">
                  <div className="kpi-label">측정 대기</div>
                  <div className="kpi-value" style={{ color: '#075985' }}>
                    {pending.length}
                    <span style={{ fontSize: 14, color: '#9ca3af', marginLeft: 2 }}>건</span>
                  </div>
                  <div className="kpi-sub">승인 후 7일 뒤 자동 측정</div>
                </div>
              </div>

              {filteredMeasured.length === 0 ? (
                <div className="empty">측정된 성과가 없습니다. 제안을 승인하고 7일 후 분석을 실행하면 측정됩니다.</div>
              ) : (
                <div className="card">
                  <div className="card-title">
                    효과 측정 이력 <span className="text-muted">({filteredMeasured.length}건)</span>
                  </div>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>측정 시각</th>
                        <th>에이전트</th>
                        <th>대상</th>
                        <th>액션</th>
                        <th>전략 모드</th>
                        <th>결과</th>
                        <th>지표 변화</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredMeasured.map(log => {
                        const vm = VERDICT_META[log.effect_verdict] ?? VERDICT_META.neutral
                        const modeColor = MODE_COLOR[log.ad_strategy_mode] ?? '#6b7280'
                        return (
                          <tr key={log.log_id}>
                            <td className="text-muted">
                              {log.effect_measured_at
                                ? new Date(log.effect_measured_at).toLocaleDateString('ko-KR')
                                : new Date(log.executed_at).toLocaleDateString('ko-KR')}
                            </td>
                            <td className="text-muted">{AGENT_LABEL[log.agent] ?? log.agent}</td>
                            <td style={{ fontWeight: 500, maxWidth: 160 }}>{log.target_name}</td>
                            <td>{log.action_type}</td>
                            <td>
                              {log.ad_strategy_mode
                                ? <span style={{ fontSize: 12, fontWeight: 700, color: modeColor }}>{log.ad_strategy_mode}</span>
                                : <span className="text-muted">-</span>}
                            </td>
                            <td><span className={`badge ${vm.cls}`}>{vm.label}</span></td>
                            <td><MetricDiff baseline={log.baseline_metrics} result={log.result_metrics} agent={log.agent} /></td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}

              {pending.length > 0 && (
                <div className="card">
                  <div className="card-title">측정 대기 중 ({pending.length}건)</div>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>승인 시각</th>
                        <th>에이전트</th>
                        <th>대상</th>
                        <th>액션</th>
                        <th>상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pending.map(log => (
                        <tr key={log.log_id}>
                          <td className="text-muted">{new Date(log.executed_at).toLocaleDateString('ko-KR')}</td>
                          <td className="text-muted">{AGENT_LABEL[log.agent] ?? log.agent}</td>
                          <td style={{ fontWeight: 500 }}>{log.target_name}</td>
                          <td>{log.action_type}</td>
                          <td><span className="badge verdict-pending">측정 대기</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </>
      )}
    </>
  )
}

function MetricDiff({ baseline, result, agent }) {
  if (!baseline || !result) return <span className="text-muted">-</span>

  const key = agent === 'ad_analyzer' ? 'monthly_total' : 'sales_count'
  const b = baseline[key]
  const r = result[key]

  if (b == null || r == null) {
    const keys = Object.keys(result).slice(0, 2)
    return (
      <div style={{ fontSize: 12 }}>
        {keys.map(k => (
          <div key={k} style={{ color: '#6b7280' }}>
            {k}: <span style={{ fontWeight: 600, color: '#1a1a1a' }}>{result[k]}</span>
          </div>
        ))}
      </div>
    )
  }

  const diff = r - b
  const pct  = b !== 0 ? ((diff / b) * 100).toFixed(1) : null
  const color = diff > 0 ? '#166534' : diff < 0 ? '#b91c1c' : '#6b7280'

  return (
    <div style={{ fontSize: 12 }}>
      <span style={{ color: '#9ca3af' }}>{b.toLocaleString()}</span>
      {' → '}
      <span style={{ fontWeight: 700, color }}>{r.toLocaleString()}</span>
      {pct != null && (
        <span style={{ color, fontWeight: 600, marginLeft: 4 }}>
          ({diff >= 0 ? '+' : ''}{pct}%)
        </span>
      )}
    </div>
  )
}
