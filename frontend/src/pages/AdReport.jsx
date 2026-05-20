import { useEffect, useState } from 'react'
import { api } from '../api'

const COMP_COLOR = {
  '높음': { color: '#e4371c', bg: '#fdecea' },
  '보통': { color: '#f59e0b', bg: '#fffbeb' },
  '낮음': { color: '#03c75a', bg: '#e6f9ee' },
}

function pct(v) { return v != null ? v.toFixed(2) + '%' : '-' }
function won(v) { return v != null ? v.toLocaleString() + '원' : '-' }
function num(v) { return v != null ? Number(v).toLocaleString() : '-' }

export default function AdReport() {
  const [kwVolume,   setKwVolume]   = useState([])
  const [adCopies,   setAdCopies]   = useState([])
  const [campaigns,  setCampaigns]  = useState([])
  const [loading,    setLoading]    = useState(true)
  const [tab,        setTab]        = useState('campaign')
  const [onlyUnbid,  setOnlyUnbid]  = useState(false)
  const [expandedCampaign, setExpandedCampaign] = useState(null)
  const [error,      setError]      = useState(null)

  useEffect(() => {
    Promise.all([
      api.getCampaigns().catch(e => { setError(e.message); return [] }),
      api.getKeywordVolume().catch(() => []),
      api.getAds().catch(() => []),
    ]).then(([cmp, kv, ads]) => {
      setCampaigns(cmp)
      setKwVolume(kv)
      setAdCopies(ads)
    }).finally(() => setLoading(false))
  }, [])

  const filteredKw = onlyUnbid ? kwVolume.filter(k => !k.is_bidding) : kwVolume

  const tabs = [
    { key: 'campaign', label: '캠페인 성과', count: campaigns.length },
    { key: 'keyword',  label: '키워드 검색량', count: kwVolume.length },
    { key: 'copy',     label: '광고 소재', count: adCopies.length },
  ]

  return (
    <>
      <div className="page-title">검색광고 보고서</div>

      <div className="suggest-tabs">
        {tabs.map(t => (
          <button
            key={t.key}
            className={`suggest-tab${tab === t.key ? ' active' : ''}`}
            style={tab === t.key ? { borderBottomColor: '#1a73e8', color: '#1a73e8' } : {}}
            onClick={() => setTab(t.key)}
          >
            {t.label}
            {t.count > 0 && (
              <span className="tab-count" style={tab === t.key ? { background: '#1a73e8' } : {}}>
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {loading && <div className="empty">불러오는 중…</div>}
      {error && <div className="card" style={{ color: '#e4371c', fontSize: 13 }}>API 오류: {error}</div>}

      {/* 캠페인 성과 탭 */}
      {!loading && tab === 'campaign' && (
        campaigns.length === 0
          ? <div className="empty">분석을 실행하면 캠페인 성과가 수집됩니다.</div>
          : <>
              {/* 캠페인 요약 카드 */}
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
                    {campaigns.length
                      ? pct(campaigns.reduce((s, c) => s + (c.ctr ?? 0), 0) / campaigns.length)
                      : '-'}
                  </div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">평균 CPC</div>
                  <div className="kpi-value">
                    {campaigns.length
                      ? won(Math.round(campaigns.reduce((s, c) => s + (c.cpc ?? 0), 0) / campaigns.length))
                      : '-'}
                  </div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">총 광고비</div>
                  <div className="kpi-value">{won(campaigns.reduce((s, c) => s + (c.spend ?? 0), 0))}</div>
                </div>
              </div>

              {/* 캠페인별 상세 */}
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
                          onClick={() => setExpandedCampaign(
                            expandedCampaign === c.campaign_id ? null : c.campaign_id
                          )}
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

      {/* 키워드 검색량 탭 */}
      {!loading && tab === 'keyword' && (
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

      {/* 광고 소재 탭 */}
      {!loading && tab === 'copy' && (
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
