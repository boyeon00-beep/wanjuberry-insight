import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function Analysis() {
  const [state, setState] = useState('idle')  // idle | running | success | error
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  async function handleStart() {
    setState('running')
    setResult(null)
    setError(null)
    try {
      const run = await api.runAnalysis()
      setResult(run)
      setState(run.status)
    } catch (e) {
      setError(e.message)
      setState('error')
    }
  }

  const collectStep = result?.steps?.find(s => s.name === 'collect')
  const analyzeStep = result?.steps?.find(s => s.name === 'analyze')

  return (
    <>
      <div className="page-title">분석</div>

      <div className="card">
        <div className="card-title">수집 → 분석 → 제안 생성</div>
        <p className="text-muted" style={{ marginBottom: 16 }}>
          버튼을 누르면 네이버 커머스 데이터 수집, AI 분석, 제안 생성을 순서대로 실행합니다.
        </p>
        <button
          className="btn btn-primary"
          onClick={handleStart}
          disabled={state === 'running'}
        >
          {state === 'running' ? '분석 중…' : '분석 시작'}
        </button>
      </div>

      {state !== 'idle' && (
        <div className={`status-bar ${state}`}>
          {state === 'running' && '분석 실행 중입니다. 잠시 기다려 주세요.'}
          {state === 'success' && '분석이 완료되었습니다.'}
          {state === 'error'   && `오류: ${error}`}
        </div>
      )}

      {result && (
        <>
          <div className="card">
            <div className="card-title">실행 결과</div>
            <table className="table">
              <tbody>
                <tr>
                  <td className="text-muted" style={{ width: 120 }}>시즌</td>
                  <td>
                    <span className={`badge season-${result.season_flag}`}>{result.season_flag}</span>
                    <span className="text-muted" style={{ marginLeft: 8 }}>{result.season_note}</span>
                  </td>
                </tr>
                <tr>
                  <td className="text-muted">수집</td>
                  <td>
                    {collectStep?.status === 'success'
                      ? `${collectStep.result?.naver_commerce?.total}개 상품`
                      : collectStep?.status}
                  </td>
                </tr>
                <tr>
                  <td className="text-muted">제안 생성</td>
                  <td>
                    {analyzeStep?.status === 'success'
                      ? `${analyzeStep.result?.total_suggestions}개 제안 생성됨`
                      : analyzeStep?.status}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {analyzeStep?.status === 'success' && (
            <div className="card">
              <div className="card-title">제안 생성 완료</div>
              <p className="text-muted" style={{ marginBottom: 16 }}>
                {analyzeStep.result.total_suggestions}개 제안이 제안함에 저장되었습니다.
              </p>
              <button
                className="btn btn-ghost"
                onClick={() => navigate('/suggestions')}
              >
                제안함으로 이동 →
              </button>
            </div>
          )}
        </>
      )}
    </>
  )
}
