import { useEffect, useState } from 'react'
import { api } from '../api'

function pct(v) { return v != null ? v.toFixed(2) + '%' : '-' }
function won(v) { return v != null ? v.toLocaleString() + '원' : '-' }
function num(v) { return v != null ? Number(v).toLocaleString() : '-' }

const COMP_COLOR = {
  '높음': { color: '#e4371c', bg: '#fdecea' },
  '보통': { color: '#f59e0b', bg: '#fffbeb' },
  '낮음': { color: '#03c75a', bg: '#e6f9ee' },
}

const TABS = [
  { key: 'products', label: '상품 목록' },
  { key: 'revenue',  label: '매출 내역' },
  { key: 'ad',       label: '광고 현황' },
  { key: 'coupang',  label: '쿠팡 현황' },
]

export default function DataStatus() {
  const [tab, setTab] = useState('products')

  const [naverProducts,    setNaverProducts]    = useState([])
  const [coupangProducts,  setCoupangProducts]  = useState([])
  const [wingAds,          setWingAds]          = useState([])
  const [campaigns,        setCampaigns]        = useState([])
  const [kwVolume,         setKwVolume]         = useState([])
  const [adCopies,         setAdCopies]         = useState([])
  const [loading,          setLoading]          = useState(true)
  const [error,            setError]            = useState(null)

  useEffect(() => {
    Promise.all([
      api.getNaverProducts().catch(() => []),
      api.getCoupangProducts().catch(() => []),
      api.getCoupangAdSummary().catch(() => []),
      api.getCampaigns().catch(e => { setError(e.message); return [] }),
      api.getKeywordVolume().catch(() => []),
      api.getAds().catch(() => []),
    ]).then(([naver, coupang, wing, cmp, kv, ads]) => {
      setNaverProducts(naver)
      setCoupangProducts(coupang)
      setWingAds(wing)
      setCampaigns(cmp)
      setKwVolume(kv)
      setAdCopies(ads)
    }).finally(() => setLoading(false))
  }, [])

  return (
    <>
      <div className="page-title">데이터 현황</div>

      <div className="suggest-tabs">
        {TABS.map(t => (
          <button
            key={t.key}
            className={`suggest-tab${tab === t.key ? ' active' : ''}`}
            style={tab === t.key ? { borderBottomColor: '#374151', color: '#374151' } : {}}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && <div className="empty">불러오는 중…</div>}
      {error && <div className="card" style={{ color: '#e4371c', fontSize: 13 }}>API 오류: {error}</div>}

      {!loading && tab === 'products' && (
        <ProductsTab naver={naverProducts} coupang={coupangProducts} />
      )}
      {!loading && tab === 'revenue' && (
        <RevenueTab naver={naverProducts} coupang={coupangProducts} />
      )}
      {!loading && tab === 'ad' && (
        <AdTab campaigns={campaigns} kwVolume={kwVolume} adCopies={adCopies} />
      )}
      {!loading && tab === 'coupang' && (
        <CoupangTab products={coupangProducts} wingAds={wingAds} />
      )}
    </>
  )
}

/* ── 상품 목록 ── */
function ProductsTab({ naver, coupang }) {
  const [platform, setPlatform] = useState('naver')
  return (
    <>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {[['naver', '네이버 스마트스토어'], ['coupang', '쿠팡']].map(([key, label]) => (
          <button
            key={key}
            className={`agent-filter-btn${platform === key ? ' active' : ''}`}
            onClick={() => setPlatform(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {platform === 'naver' && (
        naver.length === 0
          ? <div className="empty">수집된 네이버 상품이 없습니다.</div>
          : <div className="card">
              <div className="card-title">네이버 스마트스토어 상품 ({naver.length}개)</div>
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
                  {naver.map(p => {
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

      {platform === 'coupang' && (
        coupang.length === 0
          ? <div className="empty">수집된 쿠팡 상품이 없습니다.</div>
          : <div className="card">
              <div className="card-title">쿠팡 상품 ({coupang.length}개)</div>
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
                  {coupang.map(p => (
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
    </>
  )
}

/* ── 매출 내역 ── */
function RevenueTab({ naver, coupang }) {
  const naverRevenue   = naver.reduce((s, p) => s + (p.sales_revenue ?? 0), 0)
  const coupangRevenue = coupang.reduce((s, p) => s + (p.sales_revenue ?? 0), 0)
  const total          = naverRevenue + coupangRevenue

  const rows = [
    ...naver.map(p => ({ ...p, platform: '네이버', platformColor: '#03c75a' })),
    ...coupang.map(p => ({ ...p, platform: '쿠팡', platformColor: '#e4371c' })),
  ].sort((a, b) => (b.sales_revenue ?? 0) - (a.sales_revenue ?? 0))

  if (rows.length === 0) return <div className="empty">수집된 매출 데이터가 없습니다.</div>

  return (
    <>
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <div className="kpi-card">
          <div className="kpi-label">전체 매출 (30일)</div>
          <div className="kpi-value">{total.toLocaleString()}원</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">네이버 매출</div>
          <div className="kpi-value" style={{ color: '#03c75a' }}>{naverRevenue.toLocaleString()}원</div>
          <div className="kpi-sub">{naver.length}개 상품</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">쿠팡 매출</div>
          <div className="kpi-value" style={{ color: '#e4371c' }}>{coupangRevenue.toLocaleString()}원</div>
          <div className="kpi-sub">{coupang.length}개 상품</div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">상품별 매출</div>
        <table className="table">
          <thead>
            <tr>
              <th>플랫폼</th>
              <th>상품명</th>
              <th style={{ textAlign: 'right' }}>판매수</th>
              <th style={{ textAlign: 'right' }}>매출</th>
              <th style={{ textAlign: 'right' }}>비중</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(p => (
              <tr key={p.platform + p.product_id}>
                <td>
                  <span style={{ fontSize: 12, fontWeight: 700, color: p.platformColor }}>
                    {p.platform}
                  </span>
                </td>
                <td style={{ fontWeight: 500 }}>{p.name}</td>
                <td style={{ textAlign: 'right' }}>{(p.sales_count ?? 0).toLocaleString()}</td>
                <td style={{ textAlign: 'right', fontWeight: 600, color: '#166534' }}>
                  {p.sales_revenue ? p.sales_revenue.toLocaleString() + '원' : '-'}
                </td>
                <td style={{ textAlign: 'right', color: '#6b7280' }}>
                  {total > 0 && p.sales_revenue
                    ? ((p.sales_revenue / total) * 100).toFixed(1) + '%'
                    : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}

/* ── 광고 현황 (네이버) ── */
function AdTab({ campaigns, kwVolume, adCopies }) {
  const [subTab, setSubTab]             = useState('campaign')
  const [onlyUnbid, setOnlyUnbid]       = useState(false)
  const [expandedCampaign, setExpanded] = useState(null)

  const filteredKw = onlyUnbid ? kwVolume.filter(k => !k.is_bidding) : kwVolume

  const subTabs = [
    { key: 'campaign', label: '캠페인 성과', count: campaigns.length },
    { key: 'keyword',  label: '키워드 검색량', count: kwVolume.length },
    { key: 'copy',     label: '광고 소재', count: adCopies.length },
  ]

  return (
    <>
      <div className="suggest-tabs">
        {subTabs.map(t => (
          <button
            key={t.key}
            className={`suggest-tab${subTab === t.key ? ' active' : ''}`}
            style={subTab === t.key ? { borderBottomColor: '#1a73e8', color: '#1a73e8' } : {}}
            onClick={() => setSubTab(t.key)}
          >
            {t.label}
            {t.count > 0 && (
              <span className="tab-count" style={subTab === t.key ? { background: '#1a73e8' } : {}}>
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {subTab === 'campaign' && (
        campaigns.length === 0
          ? <div className="empty">분석을 실행하면 캠페인 성과가 수집됩니다.</div>
          : <>
              <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
                <div className="kpi-card">
                  <div className="kpi-label">총 노출수</div>
                  <div className="kpi-value">{num(campaigns.reduce((s, c) => s + (c.impressions ?? 0), 0))}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">총 클릭수</div>
                  <div className="kpi-value">{num(campaigns.reduce((s, c) => s + (c.clicks ?? 0), 0))}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">평균 CTR</div>
                  <div className="kpi-value">
                    {campaigns.length ? pct(campaigns.reduce((s, c) => s + (c.ctr ?? 0), 0) / campaigns.length) : '-'}
                  </div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">평균 CPC</div>
                  <div className="kpi-value">
                    {campaigns.length ? won(Math.round(campaigns.reduce((s, c) => s + (c.cpc ?? 0), 0) / campaigns.length)) : '-'}
                  </div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">총 광고비</div>
                  <div className="kpi-value">{won(campaigns.reduce((s, c) => s + (c.spend ?? 0), 0))}</div>
                </div>
              </div>

              <div className="card">
                <div className="card-title">캠페인별 성과</div>
                <table className="table">
                  <thead>
                    <tr>
                      <th>캠페인명</th>
                      <th>상태</th>
                      <th style={{ textAlign: 'right' }}>일예산</th>
                      <th style={{ textAlign: 'right' }}>광고비</th>
                      <th style={{ textAlign: 'right' }}>노출</th>
                      <th style={{ textAlign: 'right' }}>클릭</th>
                      <th style={{ textAlign: 'right' }}>CTR</th>
                      <th style={{ textAlign: 'right' }}>CPC</th>
                      <th style={{ textAlign: 'right' }}>전환금액</th>
                      <th style={{ textAlign: 'right' }}>ROAS</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {campaigns.map(c => (
                      <>
                        <tr
                          key={c.campaign_id}
                          style={{ cursor: 'pointer' }}
                          onClick={() => setExpanded(expandedCampaign === c.campaign_id ? null : c.campaign_id)}
                        >
                          <td style={{ fontWeight: 600 }}>{c.campaign_name}</td>
                          <td>
                            <span className={`badge ${c.status === '운영중' ? 'badge-approved' : 'badge-skipped'}`}>
                              {c.status}
                            </span>
                          </td>
                          <td style={{ textAlign: 'right' }}>{won(c.budget_daily)}</td>
                          <td style={{ textAlign: 'right', fontWeight: 600 }}>{won(c.spend)}</td>
                          <td style={{ textAlign: 'right' }}>{num(c.impressions)}</td>
                          <td style={{ textAlign: 'right' }}>{num(c.clicks)}</td>
                          <td style={{ textAlign: 'right', fontWeight: 600, color: (c.ctr ?? 0) >= 2 ? '#166534' : 'inherit' }}>
                            {pct(c.ctr)}
                          </td>
                          <td style={{ textAlign: 'right' }}>{won(c.cpc)}</td>
                          <td style={{ textAlign: 'right' }}>{won(c.conversions)}</td>
                          <td style={{ textAlign: 'right', fontWeight: 600 }}>
                            {c.roas != null ? c.roas.toFixed(1) : '-'}
                          </td>
                          <td style={{ textAlign: 'right', color: '#9ca3af', fontSize: 12 }}>
                            {expandedCampaign === c.campaign_id ? '▲' : '▼'} 키워드
                          </td>
                        </tr>
                        {expandedCampaign === c.campaign_id && (c.keywords ?? []).length > 0 && (
                          <tr key={c.campaign_id + '_kw'}>
                            <td colSpan={11} style={{ background: '#f9fafb', padding: '12px 16px' }}>
                              <table className="table" style={{ margin: 0 }}>
                                <thead>
                                  <tr>
                                    <th>키워드</th>
                                    <th style={{ textAlign: 'right' }}>입찰가</th>
                                    <th style={{ textAlign: 'right' }}>평균순위</th>
                                    <th style={{ textAlign: 'right' }}>CTR</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {c.keywords.map(kw => (
                                    <tr key={kw.keyword}>
                                      <td style={{ fontWeight: 500 }}>{kw.keyword}</td>
                                      <td style={{ textAlign: 'right' }}>{won(kw.bid)}</td>
                                      <td style={{ textAlign: 'right' }}>{kw.rank != null ? kw.rank.toFixed(1) : '-'}</td>
                                      <td style={{ textAlign: 'right' }}>{pct(kw.score)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
      )}

      {subTab === 'keyword' && (
        kwVolume.length === 0
          ? <div className="empty">분석을 실행하면 키워드 검색량이 수집됩니다.</div>
          : <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <div className="card-title" style={{ marginBottom: 0 }}>
                  키워드 월간 검색량 <span className="text-muted">({filteredKw.length}개)</span>
                </div>
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, cursor: 'pointer' }}>
                  <input type="checkbox" checked={onlyUnbid} onChange={e => setOnlyUnbid(e.target.checked)} />
                  미입찰만
                </label>
              </div>
              <table className="table">
                <thead>
                  <tr>
                    <th>키워드</th>
                    <th style={{ textAlign: 'right' }}>월간 합계</th>
                    <th style={{ textAlign: 'right' }}>PC</th>
                    <th style={{ textAlign: 'right' }}>모바일</th>
                    <th>경쟁도</th>
                    <th>입찰</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredKw.map(k => {
                    const comp = COMP_COLOR[k.competition] ?? { color: '#888', bg: '#f5f5f5' }
                    return (
                      <tr key={k.id ?? k.keyword}>
                        <td style={{ fontWeight: 500 }}>{k.keyword}</td>
                        <td style={{ textAlign: 'right', fontWeight: 700 }}>{num(k.monthly_total)}</td>
                        <td style={{ textAlign: 'right', color: '#666' }}>{num(k.monthly_pc)}</td>
                        <td style={{ textAlign: 'right', color: '#666' }}>{num(k.monthly_mobile)}</td>
                        <td>
                          <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 12, color: comp.color, background: comp.bg, fontWeight: 500 }}>
                            {k.competition || '-'}
                          </span>
                        </td>
                        <td>
                          {k.is_bidding
                            ? <span className="badge badge-approved">입찰중</span>
                            : <span className="badge badge-pending">미입찰</span>}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
      )}

      {subTab === 'copy' && (
        adCopies.length === 0
          ? <div className="empty">분석을 실행하면 광고 소재가 수집됩니다.</div>
          : <div className="card">
              <div className="card-title">광고 소재 (카피)</div>
              <table className="table">
                <thead>
                  <tr>
                    <th>헤드라인</th>
                    <th>설명문 1</th>
                    <th>설명문 2</th>
                    <th>상태</th>
                  </tr>
                </thead>
                <tbody>
                  {adCopies.map(c => (
                    <tr key={c.ad_id}>
                      <td style={{ fontWeight: 600 }}>{c.headline || '-'}</td>
                      <td className="text-muted">{c.description1 || '-'}</td>
                      <td className="text-muted">{c.description2 || '-'}</td>
                      <td>
                        <span className={`badge ${c.status === '운영중' ? 'badge-approved' : 'badge-pending'}`}>
                          {c.status || '-'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
      )}
    </>
  )
}

/* ── 쿠팡 현황 ── */
function CoupangTab({ products, wingAds }) {
  const period = wingAds.length > 0
    ? `${wingAds[0].report_from} ~ ${wingAds[0].report_to}`
    : ''

  const totalCost    = wingAds.reduce((s, r) => s + (r.ad_cost ?? 0), 0)
  const totalClicks  = wingAds.reduce((s, r) => s + (r.clicks ?? 0), 0)
  const totalOrders  = wingAds.reduce((s, r) => s + (r.orders_14d ?? 0), 0)
  const totalRevenue = wingAds.reduce((s, r) => s + (r.conversion_revenue_14d ?? 0), 0)
  const totalRoas    = totalCost > 0 ? Math.round(totalRevenue / totalCost * 100) : null

  return (
    <>
      {products.length > 0 && (
        <div className="card">
          <div className="card-title">쿠팡 상품 ({products.length}개)</div>
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
              {products.map(p => (
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

      {wingAds.length === 0 ? (
        <div className="empty">Wing 광고 보고서를 설정에서 업로드하면 표시됩니다.</div>
      ) : (
        <div className="card">
          <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>쿠팡 Wing 광고 현황</span>
            <span className="text-muted" style={{ fontSize: 12, fontWeight: 400 }}>{period}</span>
          </div>

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
      )}
    </>
  )
}
