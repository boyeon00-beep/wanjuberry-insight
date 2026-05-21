import { useEffect, useState } from 'react'
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

function strategyMode(seasonFlag) {
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

function KpiCard({ label, value, sub, accent }) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={accent ? { color: accent } : {}}>{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  )
}

export default function Dashboard() {
  const [lastRun, setLastRun]               = useState(null)
  const [naverProducts, setNaverProducts]   = useState([])
  const [coupangProducts, setCoupangProducts] = useState([])
  const [wingAds, setWingAds]               = useState([])
  const [suggestions, setSuggestions]       = useState([])
  const [loading, setLoading]               = useState(true)

  useEffect(() => {
    Promise.all([
      api.getRuns().catch(() => []),
      api.getNaverProducts().catch(() => []),
      api.getCoupangProducts().catch(() => []),
      api.getCoupangAdSummary().catch(() => []),
      api.getSuggestions().catch(() => []),
    ]).then(([runs, naver, coupang, wing, suggs]) => {
      setLastRun(runs[0] ?? null)
      setNaverProducts(naver)
      setCoupangProducts(coupang)
      setWingAds(wing)
      setSuggestions(suggs)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <><div className="page-title">대시보드</div><div className="empty">불러오는 중…</div></>

  if (!lastRun) {
    return (
      <>
        <div className="page-title">대시보드</div>
        <div className="empty">분석 실행 이력이 없습니다. 분석 메뉴에서 시작하세요.</div>
      </>
    )
  }

  const naverRevenue  = naverProducts.reduce((s, p) => s + (p.sales_revenue ?? 0), 0)
  const coupangRevenue = coupangProducts.reduce((s, p) => s + (p.sales_revenue ?? 0), 0)
  const pendingCount  = suggestions.filter(s => s.status === 'pending').length
  const approvedCount = suggestions.filter(s => s.status === 'approved').length
  const rejectedCount = suggestions.filter(s => s.status === 'rejected').length

  const mode = strategyMode(lastRun.season_flag)
  const modeStyle = STRATEGY_LABEL[mode] ?? STRATEGY_LABEL.PREPARE
  const coupangMode = coupangStrategyMode(coupangProducts, wingAds)
  const coupangModeStyle = STRATEGY_LABEL[coupangMode] ?? STRATEGY_LABEL.READY_CHECK

  return (
    <>
      <div className="page-title">대시보드</div>

      {/* KPI 카드 */}
      <div className="kpi-grid">
        <KpiCard
          label="네이버 매출 (30일)"
          value={naverRevenue ? naverRevenue.toLocaleString() + '원' : '-'}
          sub={`${naverProducts.length}개 상품`}
        />
        <KpiCard
          label="쿠팡 매출 (30일)"
          value={coupangRevenue ? coupangRevenue.toLocaleString() + '원' : '-'}
          sub={`${coupangProducts.length}개 상품`}
        />
        <KpiCard
          label="대기 중인 제안"
          value={pendingCount + '개'}
          sub={`승인 ${approvedCount} / 거절 ${rejectedCount}`}
          accent={pendingCount > 0 ? '#854d0e' : undefined}
        />
        <div className="kpi-card">
          <div className="kpi-label">현재 전략 모드</div>
          <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 11, color: '#6b7280', width: 40 }}>네이버</span>
              <span style={{
                padding: '3px 10px', borderRadius: 20, fontSize: 13, fontWeight: 700,
                color: modeStyle.color, background: modeStyle.bg,
              }}>{modeStyle.label}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 11, color: '#6b7280', width: 40 }}>쿠팡</span>
              <span style={{
                padding: '3px 10px', borderRadius: 20, fontSize: 13, fontWeight: 700,
                color: coupangModeStyle.color, background: coupangModeStyle.bg,
              }}>{coupangModeStyle.label}</span>
            </div>
          </div>
          <div className="kpi-sub" style={{ marginTop: 6 }}>
            {lastRun.season_flag} · {lastRun.season_note}
          </div>
        </div>
      </div>

      {/* 마지막 분석 정보 */}
      <div className="card">
        <div className="card-title">마지막 분석</div>
        <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
          <div>
            <div className="text-muted" style={{ marginBottom: 2 }}>실행 시각</div>
            <div style={{ fontWeight: 600 }}>{new Date(lastRun.started_at).toLocaleString('ko-KR')}</div>
          </div>
          <div>
            <div className="text-muted" style={{ marginBottom: 2 }}>상태</div>
            <span className={`badge badge-${lastRun.status === 'success' ? 'approved' : 'rejected'}`}>
              {lastRun.status}
            </span>
          </div>
          <div>
            <div className="text-muted" style={{ marginBottom: 2 }}>시즌</div>
            <span className={`badge season-${lastRun.season_flag}`}>{lastRun.season_flag}</span>
          </div>
        </div>
      </div>

      {/* 네이버 상품 현황 */}
      {naverProducts.length > 0 && (
        <div className="card">
          <div className="card-title">네이버 스마트스토어 상품</div>
          <table className="table">
            <thead>
              <tr>
                <th>상품명</th>
                <th style={{ textAlign: 'right' }}>가격</th>
                <th style={{ textAlign: 'right' }}>판매수</th>
                <th style={{ textAlign: 'right' }}>매출</th>
                <th style={{ textAlign: 'right' }}>리뷰</th>
                <th style={{ textAlign: 'right' }}>재고</th>
                <th>유형</th>
              </tr>
            </thead>
            <tbody>
              {naverProducts.map(p => {
                const stock = (p.options ?? []).reduce((s, o) => s + (o.stock ?? 0), 0)
                return (
                  <tr key={p.product_id}>
                    <td style={{ fontWeight: 500, maxWidth: 220 }}>{p.name}</td>
                    <td style={{ textAlign: 'right' }}>{(p.price ?? 0).toLocaleString()}원</td>
                    <td style={{ textAlign: 'right', fontWeight: 600 }}>{(p.sales_count ?? 0).toLocaleString()}</td>
                    <td style={{ textAlign: 'right', fontWeight: 600, color: '#166534' }}>
                      {p.sales_revenue ? p.sales_revenue.toLocaleString() + '원' : '-'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {p.review_score} <span className="text-muted">({p.review_count})</span>
                    </td>
                    <td style={{ textAlign: 'right', color: stock === 0 ? '#b91c1c' : 'inherit', fontWeight: stock === 0 ? 600 : 400 }}>
                      {stock === 0 ? '품절' : stock.toLocaleString() + '개'}
                    </td>
                    <td><span className="badge badge-pending">{p.product_type}</span></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 쿠팡 상품 현황 */}
      {coupangProducts.length > 0 && (
        <div className="card">
          <div className="card-title">쿠팡 상품</div>
          <table className="table">
            <thead>
              <tr>
                <th>상품명</th>
                <th style={{ textAlign: 'right' }}>가격</th>
                <th style={{ textAlign: 'right' }}>판매수</th>
                <th style={{ textAlign: 'right' }}>매출</th>
                <th>유형</th>
              </tr>
            </thead>
            <tbody>
              {coupangProducts.map(p => (
                <tr key={p.product_id}>
                  <td style={{ fontWeight: 500 }}>{p.name}</td>
                  <td style={{ textAlign: 'right' }}>{p.price ? p.price.toLocaleString() + '원' : '-'}</td>
                  <td style={{ textAlign: 'right', fontWeight: 600 }}>{(p.sales_count ?? 0).toLocaleString()}</td>
                  <td style={{ textAlign: 'right', fontWeight: 600, color: '#166534' }}>
                    {p.sales_revenue ? p.sales_revenue.toLocaleString() + '원' : '-'}
                  </td>
                  <td><span className="badge badge-pending">{p.product_type}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 쿠팡 Wing 광고 현황 */}
      {wingAds.length > 0 && <WingAdTable wingAds={wingAds} />}

      {/* 제안 현황 */}
      {suggestions.length > 0 && (
        <div className="card">
          <div className="card-title">제안 현황</div>
          <SuggestionStats suggestions={suggestions} />
        </div>
      )}
    </>
  )
}

function WingAdTable({ wingAds }) {
  // 가장 최근 업로드 기간 표시
  const period = wingAds.length > 0
    ? `${wingAds[0].report_from} ~ ${wingAds[0].report_to}`
    : ''

  const totalCost    = wingAds.reduce((s, r) => s + (r.ad_cost ?? 0), 0)
  const totalClicks  = wingAds.reduce((s, r) => s + (r.clicks ?? 0), 0)
  const totalOrders  = wingAds.reduce((s, r) => s + (r.orders_14d ?? 0), 0)
  const totalRevenue = wingAds.reduce((s, r) => s + (r.conversion_revenue_14d ?? 0), 0)
  const totalRoas    = totalCost > 0 ? Math.round(totalRevenue / totalCost * 100) : null

  return (
    <div className="card">
      <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>쿠팡 Wing 광고 현황</span>
        <span className="text-muted" style={{ fontSize: 12, fontWeight: 400 }}>{period}</span>
      </div>

      {/* 합계 KPI */}
      <div style={{ display: 'flex', gap: 24, marginBottom: 16, flexWrap: 'wrap' }}>
        {[
          { label: '총 광고비',   value: totalCost.toLocaleString() + '원' },
          { label: '총 클릭',     value: totalClicks.toLocaleString() },
          { label: '총 전환수',   value: totalOrders.toLocaleString(), alert: totalOrders === 0 && totalClicks > 0 },
          { label: '전환 매출',   value: totalRevenue ? totalRevenue.toLocaleString() + '원' : '-' },
          { label: '전체 ROAS',   value: totalRoas != null ? totalRoas + '%' : '-', alert: totalRoas != null && totalRoas < 100 },
        ].map(({ label, value, alert }) => (
          <div key={label}>
            <div className="text-muted" style={{ fontSize: 11, marginBottom: 2 }}>{label}</div>
            <div style={{ fontWeight: 700, fontSize: 15, color: alert ? '#b91c1c' : 'inherit' }}>{value}</div>
          </div>
        ))}
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>상품명</th>
            <th style={{ textAlign: 'right' }}>노출</th>
            <th style={{ textAlign: 'right' }}>클릭</th>
            <th style={{ textAlign: 'right' }}>광고비</th>
            <th style={{ textAlign: 'right' }}>전환수</th>
            <th style={{ textAlign: 'right' }}>전환매출</th>
            <th style={{ textAlign: 'right' }}>ROAS</th>
          </tr>
        </thead>
        <tbody>
          {wingAds.map((r, i) => {
            const defend = r.clicks > 0 && r.orders_14d === 0 && r.ad_cost > 0
            return (
              <tr key={i} style={defend ? { background: '#fff5f5' } : {}}>
                <td style={{ fontWeight: 500, maxWidth: 200 }}>{r.product_name}</td>
                <td style={{ textAlign: 'right', color: '#6b7280' }}>{(r.impressions ?? 0).toLocaleString()}</td>
                <td style={{ textAlign: 'right' }}>{(r.clicks ?? 0).toLocaleString()}</td>
                <td style={{ textAlign: 'right' }}>{(r.ad_cost ?? 0).toLocaleString()}원</td>
                <td style={{ textAlign: 'right', fontWeight: 600, color: defend ? '#b91c1c' : 'inherit' }}>
                  {r.orders_14d ?? 0}
                </td>
                <td style={{ textAlign: 'right', color: '#166534' }}>
                  {r.conversion_revenue_14d ? r.conversion_revenue_14d.toLocaleString() + '원' : '-'}
                </td>
                <td style={{ textAlign: 'right', fontWeight: 700, color: r.roas_14d != null && r.roas_14d < 100 ? '#b91c1c' : '#166534' }}>
                  {r.roas_14d != null ? r.roas_14d + '%' : '-'}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      <p className="text-muted" style={{ marginTop: 8, fontSize: 11 }}>
        빨간 행: 클릭 있으나 전환 0 (DEFEND 모드 트리거 조건)
      </p>
    </div>
  )
}

function SuggestionStats({ suggestions }) {
  const byAgent = {
    product_analyzer: suggestions.filter(s => s.agent === 'product_analyzer'),
    ad_analyzer:      suggestions.filter(s => s.agent === 'ad_analyzer'),
    coupang_analyzer: suggestions.filter(s => s.agent === 'coupang_analyzer'),
  }

  const AGENT_LABEL = {
    product_analyzer:  { label: '스마트스토어', color: '#03c75a' },
    ad_analyzer:       { label: '검색광고',     color: '#1a73e8' },
    coupang_analyzer:  { label: '쿠팡',         color: '#e4371c' },
  }

  return (
    <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
      {Object.entries(byAgent).map(([agent, items]) => {
        const info = AGENT_LABEL[agent]
        const pending  = items.filter(s => s.status === 'pending').length
        const approved = items.filter(s => s.status === 'approved').length
        const rejected = items.filter(s => s.status === 'rejected').length
        const expired  = items.filter(s => s.status === 'expired').length

        return (
          <div key={agent} style={{ minWidth: 160 }}>
            <div style={{ fontWeight: 700, color: info.color, marginBottom: 10, fontSize: 13 }}>
              {info.label}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {[
                { label: '대기', count: pending,  cls: 'badge-pending' },
                { label: '승인', count: approved, cls: 'badge-approved' },
                { label: '거절', count: rejected, cls: 'badge-rejected' },
                { label: '만료', count: expired,  cls: 'badge-skipped' },
              ].map(({ label, count, cls }) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ width: 32, textAlign: 'right', fontWeight: 700 }}>{count}</span>
                  <span className={`badge ${cls}`}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
