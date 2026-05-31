import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

function WingUploadSection() {
  const [summary, setSummary]   = useState(null)
  const [file, setFile]         = useState(null)
  const [loading, setLoading]   = useState(false)
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState(null)
  const fileRef                 = useRef(null)

  useEffect(() => {
    api.getCoupangAdSummary()
      .then(data => setSummary(data?.length ? data[0] : null))
      .catch(() => {})
  }, [result])

  async function upload() {
    if (!file) return
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await api.uploadCoupangAdReport(fd)
      setResult(res)
      setFile(null)
      if (fileRef.current) fileRef.current.value = ''
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ borderLeft: '3px solid #e4371c' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8 }}>
        <div>
          <div className="card-title" style={{ marginBottom: 4 }}>쿠팡 Wing 광고 보고서</div>
          <p className="text-muted" style={{ fontSize: 13, margin: 0 }}>
            {summary
              ? <>최근 업로드: <strong>{summary.report_from} ~ {summary.report_to}</strong> · {summary.product_name ?? ''}</>
              : '업로드된 보고서 없음 — 쿠팡 분석 시 광고 데이터가 반영되지 않습니다.'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          {error  && <span style={{ fontSize: 12, color: '#e53e3e' }}>{error}</span>}
          {result && <span style={{ fontSize: 12, color: '#38a169' }}>저장 {result.saved}건 · {result.report_from} ~ {result.report_to}</span>}
          <input
            ref={fileRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={e => setFile(e.target.files[0] ?? null)}
            style={{ fontSize: 12 }}
          />
          <button
            className="btn btn-primary"
            style={{ fontSize: 13, padding: '6px 14px' }}
            onClick={upload}
            disabled={loading || !file}
          >
            {loading ? '업로드 중…' : '업로드'}
          </button>
        </div>
      </div>
    </div>
  )
}

const PLATFORM = {
  product_analyzer: { label: '네이버 스마트스토어', color: '#03c75a', bg: '#e6f9ee' },
  ad_analyzer:      { label: '네이버 검색광고',     color: '#1a73e8', bg: '#e8f0fe' },
  coupang_analyzer: { label: '쿠팡',               color: '#e4371c', bg: '#fdecea' },
}

function PlatformSection({ agentKey, total, items }) {
  const [open, setOpen] = useState(false)
  const meta = PLATFORM[agentKey]
  if (!meta) return null

  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, marginBottom: 12, overflow: 'hidden' }}>
      <div
        style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '14px 16px', cursor: 'pointer', background: open ? '#fafafa' : '#fff',
        }}
        onClick={() => setOpen(o => !o)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{
            padding: '2px 10px', borderRadius: 12, fontSize: 12, fontWeight: 700,
            color: meta.color, background: meta.bg,
          }}>{meta.label}</span>
          <span style={{ fontWeight: 600, fontSize: 14 }}>
            {total > 0 ? `${total}개 제안 생성` : '제안 없음'}
          </span>
        </div>
        <span style={{ fontSize: 12, color: '#9ca3af' }}>{open ? '▲ 접기' : '▼ 자세히 보기'}</span>
      </div>

      {open && (
        <div style={{ padding: '0 16px 14px', borderTop: '1px solid #f0f0f0' }}>
          {items && items.length > 0 ? (
            items.map((s, i) => (
              <div key={i} style={{ padding: '10px 0', borderBottom: i < items.length - 1 ? '1px solid #f5f5f5' : 'none' }}>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginBottom: 4, flexWrap: 'wrap' }}>
                  <span className={`badge badge-${s.priority}`}>{s.priority}</span>
                  <strong style={{ fontSize: 13 }}>{s.action_type}</strong>
                  <span style={{ fontSize: 13, color: '#555' }}>{s.target_name}</span>
                </div>
                <div className="text-muted" style={{ fontSize: 13 }}>{s.reason}</div>
              </div>
            ))
          ) : (
            <p className="text-muted" style={{ marginTop: 12, fontSize: 13 }}>
              제안 내용은 제안함에서 확인하세요.
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default function Analysis() {
  const [state, setState]     = useState('idle')
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)
  const [suggestions, setSuggestions] = useState([])
  const navigate = useNavigate()

  async function handleStart() {
    setState('running')
    setResult(null)
    setError(null)
    setSuggestions([])
    try {
      const run = await api.runAnalysis()
      setResult(run)
      setState(run.status)
      if (run.status === 'success') {
        const suggs = await api.getSuggestions().catch(() => [])
        setSuggestions(suggs.filter(s => s.status === 'pending'))
      }
    } catch (e) {
      setError(e.message)
      setState('error')
    }
  }

  const collectStep = result?.steps?.find(s => s.name === 'collect')
  const analyzeStep = result?.steps?.find(s => s.name === 'analyze')

  const agentOrder = ['product_analyzer', 'ad_analyzer', 'coupang_analyzer']
  const analyzeResult = analyzeStep?.result ?? {}

  function getSuggestionsByAgent(agent) {
    return suggestions.filter(s => s.agent === agent)
  }

  return (
    <>
      <div className="page-title">분석</div>

      <WingUploadSection />

      <div className="card">
        <div className="card-title">수집 → 분석 → 제안 생성</div>
        <p className="text-muted" style={{ marginBottom: 16 }}>
          버튼을 누르면 네이버 커머스·광고, 쿠팡 데이터 수집, AI 분석, 제안 생성을 순서대로 실행합니다.
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
          {state === 'error'   && `오류: ${error ?? result?.error ?? '알 수 없는 오류'}`}
        </div>
      )}

      {result && (
        <>
          {/* 수집 요약 */}
          <div className="card">
            <div className="card-title">수집 결과</div>
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
              <div>
                <div className="text-muted" style={{ fontSize: 12, marginBottom: 2 }}>시즌</div>
                <span className={`badge season-${result.season_flag}`}>{result.season_flag}</span>
                <span className="text-muted" style={{ marginLeft: 8, fontSize: 13 }}>{result.season_note}</span>
              </div>
              <div>
                <div className="text-muted" style={{ fontSize: 12, marginBottom: 2 }}>네이버</div>
                <span style={{ fontWeight: 600, fontSize: 13 }}>
                  {collectStep?.status === 'success'
                    ? `상품 ${collectStep.result?.naver_commerce?.total ?? 0}개 · 광고소재 ${collectStep.result?.naver_ad?.total_ad_copies ?? 0}개`
                    : collectStep?.status ?? '-'}
                </span>
              </div>
              <div>
                <div className="text-muted" style={{ fontSize: 12, marginBottom: 2 }}>쿠팡</div>
                <span style={{ fontWeight: 600, fontSize: 13 }}>
                  {collectStep?.status === 'success'
                    ? (() => {
                        const c = collectStep.result?.coupang
                        if (!c || c.mode === 'skip') return '미설정'
                        return `상품 ${c.total ?? 0}개`
                      })()
                    : collectStep?.status ?? '-'}
                </span>
              </div>
            </div>
          </div>

          {/* AI 종합 판단 요약 */}
          {analyzeStep?.status === 'success' && (
            <div className="card">
              <div className="card-title" style={{ marginBottom: 4 }}>
                AI 종합 판단 요약
                <span className="text-muted" style={{ fontSize: 13, fontWeight: 400, marginLeft: 8 }}>
                  총 {analyzeResult.total_suggestions ?? 0}개 제안
                </span>
              </div>
              <p className="text-muted" style={{ fontSize: 13, marginBottom: 16 }}>
                플랫폼별 제안 내용입니다. "자세히 보기"로 펼쳐서 확인하세요.
              </p>

              {agentOrder.map(agent => {
                const keyMap = {
                  product_analyzer: 'product',
                  ad_analyzer: 'ad',
                  coupang_analyzer: 'coupang',
                }
                const total = analyzeResult[keyMap[agent]]?.total ?? 0
                const items = getSuggestionsByAgent(agent)
                return (
                  <PlatformSection
                    key={agent}
                    agentKey={agent}
                    total={total}
                    items={items}
                  />
                )
              })}

              <button
                className="btn btn-ghost"
                style={{ marginTop: 8 }}
                onClick={() => navigate('/suggestions')}
              >
                제안함에서 승인/거절 →
              </button>
            </div>
          )}
        </>
      )}
    </>
  )
}
