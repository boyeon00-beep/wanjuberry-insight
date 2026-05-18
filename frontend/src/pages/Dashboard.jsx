import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Dashboard() {
  const [lastRun, setLastRun] = useState(null)

  useEffect(() => {
    api.getRuns()
      .then(runs => setLastRun(runs.at(-1) ?? null))
      .catch(() => {})
  }, [])

  if (!lastRun) {
    return (
      <>
        <div className="page-title">대시보드</div>
        <div className="empty">분석 실행 이력이 없습니다. 분석 메뉴에서 시작하세요.</div>
      </>
    )
  }

  const collectStep = lastRun.steps?.find(s => s.name === 'collect')
  const analyzeStep = lastRun.steps?.find(s => s.name === 'analyze')
  const products = collectStep?.result?.naver_commerce?.products ?? []

  return (
    <>
      <div className="page-title">대시보드</div>

      <div className="card">
        <div className="card-title">마지막 분석</div>
        <table className="table">
          <tbody>
            <tr>
              <td className="text-muted" style={{ width: 120 }}>실행 시각</td>
              <td>{new Date(lastRun.started_at).toLocaleString('ko-KR')}</td>
            </tr>
            <tr>
              <td className="text-muted">시즌</td>
              <td>
                <span className={`badge season-${lastRun.season_flag}`}>
                  {lastRun.season_flag}
                </span>
                <span className="text-muted" style={{ marginLeft: 8 }}>{lastRun.season_note}</span>
              </td>
            </tr>
            <tr>
              <td className="text-muted">제안 수</td>
              <td>{analyzeStep?.result?.total_suggestions ?? '-'}개</td>
            </tr>
          </tbody>
        </table>
      </div>

      {products.length > 0 && (
        <div className="card">
          <div className="card-title">수집 상품 현황 (네이버 커머스)</div>
          <table className="table">
            <thead>
              <tr>
                <th>상품명</th>
                <th>가격</th>
                <th>판매수</th>
                <th>리뷰</th>
                <th>재고</th>
                <th>상품유형</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => {
                const stock = p.options.reduce((s, o) => s + o.stock, 0)
                return (
                  <tr key={p.product_id}>
                    <td>{p.name}</td>
                    <td>{p.price.toLocaleString()}원</td>
                    <td>{p.sales_count.toLocaleString()}</td>
                    <td>{p.review_score} ({p.review_count})</td>
                    <td style={{ color: stock === 0 ? '#b91c1c' : 'inherit' }}>
                      {stock === 0 ? '품절' : `${stock}개`}
                    </td>
                    <td>{p.domain.product_type}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
