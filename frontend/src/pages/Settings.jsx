import { useEffect, useState } from 'react'
import { api } from '../api'

const API_KEYS = [
  { key: 'ANTHROPIC_API_KEY',      label: 'Claude API' },
  { key: 'NAVER_COMMERCE_API_KEY', label: '네이버 커머스 API' },
  { key: 'NAVER_AD_API_KEY',       label: '네이버 광고 API' },
  { key: 'COUPANG_API_KEY',        label: '쿠팡 API' },
  { key: 'SUPABASE_URL',           label: 'Supabase' },
]

export default function Settings() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    api.health()
      .then(setHealth)
      .catch(() => setHealth({ status: 'error' }))
  }, [])

  return (
    <>
      <div className="page-title">설정</div>

      <div className="card">
        <div className="card-title">서버 연결 상태</div>
        {health === null && <span className="text-muted">확인 중…</span>}
        {health?.status === 'ok' && (
          <span className="badge badge-approved">백엔드 정상</span>
        )}
        {health?.status === 'error' && (
          <span className="badge badge-rejected">백엔드 연결 실패</span>
        )}
      </div>

      <div className="card">
        <div className="card-title">API 연결 상태</div>
        <p className="text-muted" style={{ marginBottom: 16 }}>
          키는 backend/.env 파일에 저장됩니다. UI에는 연결 상태만 표시됩니다.
        </p>
        <table className="table">
          <thead>
            <tr>
              <th>API</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            {API_KEYS.map(({ key, label }) => (
              <tr key={key}>
                <td>{label}</td>
                <td>
                  <span className="badge badge-pending">설정 확인 전</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="text-muted mt-16">Phase 3에서 실제 연결 테스트가 추가됩니다.</p>
      </div>
    </>
  )
}
