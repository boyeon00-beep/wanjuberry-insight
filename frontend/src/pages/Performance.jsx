import { useEffect, useState } from 'react'
import { api } from '../api'

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
  const pct = b !== 0 ? ((diff / b) * 100).toFixed(1) : null
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

export default function Performance() {
  const [logs, setLogs]       = useState([])
  const [loading, setLoading] = useState(true)
  const [agentFilter, setAgentFilter] = useState('all')

  useEffect(() => {
    api.getActionLogs()
      .then(data => setLogs([...data].reverse()))
      .finally(() => setLoading(false))
  }, [])

  const measured = logs.filter(l => l.effect_verdict && l.effect_verdict !== 'pending')
  const pending  = logs.filter(l => l.effect_verdict === 'pending')

  const counts = measured.reduce((acc, l) => {
    acc[l.effect_verdict] = (acc[l.effect_verdict] ?? 0) + 1
    return acc
  }, {})

  const filtered = (agentFilter === 'all' ? measured : measured.filter(l => l.agent === agentFilter))

  if (loading) return <><div className="page-title">성과 추적</div><div className="empty">불러오는 중…</div></>

  return (
    <>
      <div className="page-title">성과 추적</div>

      {/* 요약 KPI */}
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
        {['positive', 'neutral', 'negative', 'unmeasurable'].map(v => (
          <div className="kpi-card" key={v}>
            <div className="kpi-label">{VERDICT_META[v].label}</div>
            <div className="kpi-value">{counts[v] ?? 0}<span style={{ fontSize: 14, color: '#9ca3af', marginLeft: 2 }}>건</span></div>
          </div>
        ))}
        <div className="kpi-card">
          <div className="kpi-label">측정 대기</div>
          <div className="kpi-value" style={{ color: '#075985' }}>
            {pending.length}<span style={{ fontSize: 14, color: '#9ca3af', marginLeft: 2 }}>건</span>
          </div>
          <div className="kpi-sub">승인 후 7일 뒤 자동 측정</div>
        </div>
      </div>

      {measured.length === 0 ? (
        <div className="empty">측정된 성과가 없습니다. 제안을 승인하고 7일 후 분석을 실행하면 측정됩니다.</div>
      ) : (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 0 }}>
              효과 측정 이력 <span className="text-muted">({filtered.length}건)</span>
            </div>
            <div className="agent-filters" style={{ marginBottom: 0 }}>
              {['all', 'product_analyzer', 'ad_analyzer', 'coupang_analyzer'].map(a => (
                <button
                  key={a}
                  className={`agent-filter-btn${agentFilter === a ? ' active' : ''}`}
                  onClick={() => setAgentFilter(a)}
                >
                  {a === 'all' ? '전체' : AGENT_LABEL[a]}
                </button>
              ))}
            </div>
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
              {filtered.map(log => {
                const vm = VERDICT_META[log.effect_verdict] ?? VERDICT_META.neutral
                const modeColor = MODE_COLOR[log.ad_strategy_mode] ?? '#6b7280'
                return (
                  <tr key={log.log_id}>
                    <td className="text-muted">
                      {log.effect_measured_at
                        ? new Date(log.effect_measured_at).toLocaleDateString('ko-KR')
                        : new Date(log.executed_at).toLocaleDateString('ko-KR')}
                    </td>
                    <td>
                      <span className="text-muted">{AGENT_LABEL[log.agent] ?? log.agent}</span>
                    </td>
                    <td style={{ fontWeight: 500, maxWidth: 160 }}>{log.target_name}</td>
                    <td>{log.action_type}</td>
                    <td>
                      {log.ad_strategy_mode
                        ? <span style={{ fontSize: 12, fontWeight: 700, color: modeColor }}>{log.ad_strategy_mode}</span>
                        : <span className="text-muted">-</span>}
                    </td>
                    <td>
                      <span className={`badge ${vm.cls}`}>{vm.label}</span>
                    </td>
                    <td>
                      <MetricDiff
                        baseline={log.baseline_metrics}
                        result={log.result_metrics}
                        agent={log.agent}
                      />
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 대기 중인 항목 */}
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
  )
}
