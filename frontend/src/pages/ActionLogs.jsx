import { useEffect, useState } from 'react'
import { api } from '../api'

const TIER_LABEL = {
  ai_auto:           'AI 자동',
  ai_after_approval: 'AI (승인 후)',
  operator_manual:   '운영자 직접',
}

export default function ActionLogs() {
  const [logs, setLogs]       = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getActionLogs()
      .then(setLogs)
      .finally(() => setLoading(false))
  }, [])

  return (
    <>
      <div className="page-title">실행 로그</div>

      {loading && <div className="empty">불러오는 중…</div>}

      {!loading && logs.length === 0 && (
        <div className="empty">실행 이력이 없습니다.</div>
      )}

      {logs.length > 0 && (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>실행 시각</th>
                <th>상품</th>
                <th>액션</th>
                <th>실행 방식</th>
                <th>결과</th>
                <th>상세</th>
              </tr>
            </thead>
            <tbody>
              {[...logs].reverse().map(log => (
                <tr key={log.log_id}>
                  <td className="text-muted">{new Date(log.executed_at).toLocaleString('ko-KR')}</td>
                  <td>{log.target_name}</td>
                  <td>{log.action_type}</td>
                  <td>{TIER_LABEL[log.execution_tier]}</td>
                  <td><span className={`badge badge-${log.status}`}>{log.status}</span></td>
                  <td className="text-muted" style={{ maxWidth: 300, wordBreak: 'break-all' }}>
                    {log.detail}
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
