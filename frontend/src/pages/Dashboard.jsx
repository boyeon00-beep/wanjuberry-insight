import { useEffect, useState } from 'react'
import { api } from '../api'

const STRATEGY_LABEL = {
  PREPARE: { label: 'PREPARE — 준비', color: '#075985', bg: '#e0f2fe' },
  TEST:    { label: 'TEST — 테스트',  color: '#854d0e', bg: '#fef9c3' },
  SCALE:   { label: 'SCALE — 확장',  color: '#166534', bg: '#dcfce7' },
  DEFEND:  { label: 'DEFEND — 방어', color: '#991b1b', bg: '#fee2e2' },
  LEARN:   { label: 'LEARN — 학습',  color: '#5b21b6', bg: '#ede9fe' },
  REVIEW:  { label: 'REVIEW — 회고', color: '#374151', bg: '#f3f4f6' },
}

function strategyMode(seasonFlag) {
  if (seasonFlag === '성수기') return 'SCALE'
  if (seasonFlag === '전환기') return 'TEST'
  return 'PREPARE'
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
  const [suggestions, setSuggestions]       = useState([])
  const [loading, setLoading]               = useState(true)

  useEffect(() => {
    Promise.all([
      api.getRuns().catch(() => []),
      api.getNaverProducts().catch(() => []),
      api.getCoupangProducts().catch(() => []),
      api.getSuggestions().catch(() => []),
    ]).then(([runs, naver, coupang, suggs]) => {
      setLastRun(runs[0] ?? null)
      setNaverProducts(naver)
      setCoupangProducts(coupang)
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
          <div style={{ marginTop: 8 }}>
            <span style={{
              padding: '4px 12px', borderRadius: 20, fontSize: 14, fontWeight: 700,
              color: modeStyle.color, background: modeStyle.bg,
            }}>{modeStyle.label}</span>
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
