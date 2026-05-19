import { useEffect, useState } from 'react'
import { api } from '../api'

const COMP_COLOR = {
  '높음': { color: '#e4371c', bg: '#fdecea' },
  '보통': { color: '#f59e0b', bg: '#fffbeb' },
  '낮음': { color: '#03c75a', bg: '#e6f9ee' },
}

export default function AdReport() {
  const [kwVolume, setKwVolume]   = useState([])
  const [adCopies, setAdCopies]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [tab, setTab]             = useState('keyword')
  const [onlyUnbid, setOnlyUnbid] = useState(false)

  useEffect(() => {
    Promise.all([api.getKeywordVolume(), api.getAds()])
      .then(([kv, ads]) => { setKwVolume(kv); setAdCopies(ads) })
      .finally(() => setLoading(false))
  }, [])

  const filteredKw = onlyUnbid ? kwVolume.filter(k => !k.is_bidding) : kwVolume

  return (
    <>
      <div className="page-title">검색광고 보고서</div>

      {/* 탭 */}
      <div className="suggest-tabs">
        <button
          className={`suggest-tab${tab === 'keyword' ? ' active' : ''}`}
          style={tab === 'keyword' ? { borderBottomColor: '#1a73e8', color: '#1a73e8' } : {}}
          onClick={() => setTab('keyword')}
        >
          키워드 검색량
          {kwVolume.length > 0 && (
            <span className="tab-count" style={tab === 'keyword' ? { background: '#1a73e8' } : {}}>
              {kwVolume.length}
            </span>
          )}
        </button>
        <button
          className={`suggest-tab${tab === 'copy' ? ' active' : ''}`}
          style={tab === 'copy' ? { borderBottomColor: '#1a73e8', color: '#1a73e8' } : {}}
          onClick={() => setTab('copy')}
        >
          광고 소재
          {adCopies.length > 0 && (
            <span className="tab-count" style={tab === 'copy' ? { background: '#1a73e8' } : {}}>
              {adCopies.length}
            </span>
          )}
        </button>
      </div>

      {loading && <div className="empty">불러오는 중…</div>}

      {/* 키워드 검색량 탭 */}
      {!loading && tab === 'keyword' && (
        <>
          {kwVolume.length === 0 ? (
            <div className="empty">분석을 실행하면 키워드 검색량이 수집됩니다.</div>
          ) : (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <div className="card-title" style={{ marginBottom: 0 }}>
                  키워드 월간 검색량
                </div>
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={onlyUnbid}
                    onChange={e => setOnlyUnbid(e.target.checked)}
                  />
                  미입찰 키워드만
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
                        <td style={{ textAlign: 'right', fontWeight: 600 }}>
                          {k.monthly_total.toLocaleString()}
                        </td>
                        <td style={{ textAlign: 'right', color: '#666' }}>
                          {k.monthly_pc.toLocaleString()}
                        </td>
                        <td style={{ textAlign: 'right', color: '#666' }}>
                          {k.monthly_mobile.toLocaleString()}
                        </td>
                        <td>
                          <span style={{
                            padding: '2px 8px', borderRadius: 4, fontSize: 12,
                            color: comp.color, background: comp.bg, fontWeight: 500,
                          }}>
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
        </>
      )}

      {/* 광고 소재 탭 */}
      {!loading && tab === 'copy' && (
        <>
          {adCopies.length === 0 ? (
            <div className="empty">분석을 실행하면 광고 소재가 수집됩니다.</div>
          ) : (
            <div className="card">
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
                      <td style={{ fontWeight: 500 }}>{c.headline || '-'}</td>
                      <td className="text-muted">{c.description1 || '-'}</td>
                      <td className="text-muted">{c.description2 || '-'}</td>
                      <td>
                        <span className={`badge badge-${c.status === '운영중' ? 'approved' : 'pending'}`}>
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
      )}
    </>
  )
}
