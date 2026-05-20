import { useEffect, useState } from 'react'
import { api } from '../api'

const TIER_LABEL = {
  ai_auto:           'AI 자동',
  ai_after_approval: 'AI (승인 후)',
  operator_manual:   '운영자 직접',
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
  const [logs, setLogs]           = useState([])
  const [loading, setLoading]     = useState(true)
  const [agentFilter, setAgentFilter] = useState('all')

  useEffect(() => {
    api.getActionLogs()
      .then(data => setLogs([...data].reverse()))
      .finally(() => setLoading(false))
  }, [])

  const filtered = agentFilter === 'all'
    ? logs
    : logs.filter(l => l.agent === agentFilter)

  return (
    <>
      <div className="page-title">실행 로그</div>

      {loading && <div className="empty">불러오는 중…</div>}

      {!loading && (
        <>
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

          {filtered.length === 0 ? (
            <div className="empty">실행 이력이 없습니다.</div>
          ) : (
            <div className="card">
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
                    <th>효과 측정</th>
                    <th>상세</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(log => {
                    const vm = log.effect_verdict ? VERDICT_META[log.effect_verdict] : null
                    const modeColor = MODE_COLOR[log.ad_strategy_mode] ?? '#6b7280'
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
        </>
      )}
    </>
  )
}
