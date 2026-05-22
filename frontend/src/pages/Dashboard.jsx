import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

const STRATEGY_LABEL = {
  PREPARE:     { label: 'PREPARE — 준비',       color: '#075985', bg: '#e0f2fe' },
  TEST:        { label: 'TEST — 테스트',         color: '#854d0e', bg: '#fef9c3' },
  SCALE:       { label: 'SCALE — 확장',          color: '#166534', bg: '#dcfce7' },
  DEFEND:      { label: 'DEFEND — 방어',         color: '#991b1b', bg: '#fee2e2' },
  READY_CHECK: { label: 'READY CHECK — 준비중',  color: '#6b7280', bg: '#f3f4f6' },
  LEARN:       { label: 'LEARN — 학습',          color: '#5b21b6', bg: '#ede9fe' },
  REVIEW:      { label: 'REVIEW — 회고',         color: '#374151', bg: '#f3f4f6' },
}

function naverStrategyMode(seasonFlag) {
  if (seasonFlag === '성수기') return 'SCALE'
  if (seasonFlag === '전환기') return 'TEST'
  return 'PREPARE'
}

function coupangStrategyMode(coupangProducts, wingAds) {
  const totalSales = coupangProducts.reduce((s, p) => s + (p.sales_count ?? 0), 0)
  let base
  if (totalSales === 0) base = 'READY_CHECK'
  else if (totalSales < 10) base = 'TEST'
  else base = 'SCALE'

  if (base !== 'READY_CHECK' && wingAds.length > 0) {
    const defend = wingAds.some(r => r.ad_cost > 0 && r.clicks > 0 && r.orders_14d === 0)
    if (defend) return 'DEFEND'
  }
  return base
}

function QuickBtn({ label, sub, to, color }) {
  const navigate = useNavigate()
  return (
    <button
      className="btn btn-ghost"
      style={{ flex: 1, minWidth: 140, textAlign: 'left', padding: '12px 16px', border: '1px solid #e5e7eb' }}
      onClick={() => navigate(to)}
    >
      <div style={{ fontWeight: 600, color: color ?? '#111', marginBottom: 2 }}>{label}</div>
      {sub && <div style={{ fontSize: 12, color: '#9ca3af' }}>{sub}</div>}
    </button>
  )
}

export default function Dashboard() {
  const [lastRun, setLastRun]                 = useState(null)
  const [coupangProducts, setCoupangProducts] = useState([])
  const [wingAds, setWingAds]                 = useState([])
  const [pendingCount, setPendingCount]       = useState(0)
  const [needsDataCount, setNeedsDataCount]   = useState(0)
  const [loading, setLoading]                 = useState(true)

  useEffect(() => {
    Promise.all([
      api.getRuns().catch(() => []),
      api.getCoupangProducts().catch(() => []),
      api.getCoupangAdSummary().catch(() => []),
      api.getSuggestions().catch(() => []),
    ]).then(([runs, coupang, wing, suggs]) => {
      setLastRun(runs[0] ?? null)
      setCoupangProducts(coupang)
      setWingAds(wing)
      setPendingCount(suggs.filter(s => s.status === 'pending' && s.validator_verdict !== 'NEEDS_DATA').length)
      setNeedsDataCount(suggs.filter(s => s.status === 'pending' && s.validator_verdict === 'NEEDS_DATA').length)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <><div className="page-title">대시보드</div><div className="empty">불러오는 중…</div></>

  const naverMode      = lastRun ? naverStrategyMode(lastRun.season_flag) : 'PREPARE'
  const coupangMode    = coupangStrategyMode(coupangProducts, wingAds)
  const naverStyle     = STRATEGY_LABEL[naverMode]
  const coupangStyle   = STRATEGY_LABEL[coupangMode]

  return (
    <>
      <div className="page-title">대시보드</div>

      {/* 전략 모드 + 시즌 */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">네이버 전략 모드</div>
          <div style={{ marginTop: 8 }}>
            <span style={{
              padding: '4px 12px', borderRadius: 20, fontSize: 14, fontWeight: 700,
              color: naverStyle.color, background: naverStyle.bg,
            }}>{naverStyle.label}</span>
          </div>
          {lastRun && (
            <div className="kpi-sub" style={{ marginTop: 6 }}>
              {lastRun.season_flag} · {lastRun.season_note}
            </div>
          )}
        </div>

        <div className="kpi-card">
          <div className="kpi-label">쿠팡 전략 모드</div>
          <div style={{ marginTop: 8 }}>
            <span style={{
              padding: '4px 12px', borderRadius: 20, fontSize: 14, fontWeight: 700,
              color: coupangStyle.color, background: coupangStyle.bg,
            }}>{coupangStyle.label}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">검토 대기 제안</div>
          <div className="kpi-value" style={pendingCount > 0 ? { color: '#854d0e' } : {}}>
            {pendingCount}<span style={{ fontSize: 14, color: '#9ca3af', marginLeft: 2 }}>개</span>
          </div>
          {needsDataCount > 0 && (
            <div className="kpi-sub">관찰 필요 {needsDataCount}개 별도</div>
          )}
        </div>

        <div className="kpi-card">
          <div className="kpi-label">마지막 분석</div>
          {lastRun ? (
            <>
              <div style={{ fontWeight: 600, marginTop: 6, fontSize: 13 }}>
                {new Date(lastRun.started_at).toLocaleString('ko-KR')}
              </div>
              <div style={{ marginTop: 4 }}>
                <span className={`badge badge-${lastRun.status === 'success' ? 'approved' : 'rejected'}`}>
                  {lastRun.status}
                </span>
              </div>
            </>
          ) : (
            <div className="kpi-sub" style={{ marginTop: 8 }}>실행 이력 없음</div>
          )}
        </div>
      </div>

      {/* 빠른 이동 */}
      <div className="card">
        <div className="card-title">빠른 이동</div>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <QuickBtn to="/data"        label="데이터 현황"  sub="수집된 원본 데이터 확인" />
          <QuickBtn to="/suggestions" label="제안함"       sub={pendingCount > 0 ? `대기 ${pendingCount}개` : '대기 없음'} color={pendingCount > 0 ? '#854d0e' : undefined} />
          <QuickBtn to="/analysis"    label="분석 시작"    sub="수집 → 분석 → 제안 실행" />
          <QuickBtn to="/action-logs" label="실행 로그"    sub="Action Log + 성과 측정" />
        </div>
      </div>
    </>
  )
}
