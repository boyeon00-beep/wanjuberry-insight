import { useEffect, useRef, useState } from 'react'
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

      <FarmProfileSection />
      <FarmConstraints />
    </>
  )
}

function FarmProfileSection() {
  const [content, setContent] = useState('')
  const [saved, setSaved]     = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getFarmProfile()
      .then(r => setContent(r.content || ''))
      .finally(() => setLoading(false))
  }, [])

  async function save() {
    await api.saveFarmProfile(content).catch(() => {})
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="card">
      <div className="card-title">농장 프로필</div>
      <p className="text-muted" style={{ marginBottom: 16 }}>
        AI가 분석 시 가장 먼저 읽는 농장 기본 정보입니다.
        재배 방식, 주요 고객층, 차별점, 현재 목표 등을 자유롭게 작성하세요.
      </p>
      {loading ? (
        <div className="text-muted">불러오는 중…</div>
      ) : (
        <>
          <textarea
            style={{
              width: '100%', minHeight: 140, padding: '10px 12px',
              border: '1px solid #ddd', borderRadius: 8, fontSize: 13,
              lineHeight: 1.6, resize: 'vertical', boxSizing: 'border-box',
              fontFamily: 'inherit',
            }}
            placeholder={`예:\n완주군 소재 베리 농가. GAP 인증 취득.\n주력: 복분자 생과(6월 중순~7월 초), 냉동 복분자(연중), 블랙베리(7~8월).\n고객층: 건강 관심 40-60대, 명절 선물 수요 큼.\n차별점: 직거래, 무방부제, 당일 수확 당일 출고.\n현재 목표: 냉동 복분자 연중 매출 안정화.`}
            value={content}
            onChange={e => setContent(e.target.value)}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 10, gap: 8, alignItems: 'center' }}>
            {saved && <span className="text-muted" style={{ fontSize: 13 }}>저장됐습니다</span>}
            <button className="btn btn-primary" onClick={save}>저장</button>
          </div>
        </>
      )}
    </div>
  )
}

function FarmConstraints() {
  const [items, setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [newText, setNewText] = useState('')
  const [editId, setEditId] = useState(null)
  const [editText, setEditText] = useState('')
  const inputRef = useRef(null)

  function load() {
    setLoading(true)
    api.getConstraints()
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function add() {
    if (!newText.trim()) return
    await api.addConstraint(newText.trim()).catch(() => {})
    setNewText('')
    load()
  }

  async function remove(id) {
    await api.deleteConstraint(id).catch(() => {})
    load()
  }

  async function saveEdit(id) {
    if (!editText.trim()) return
    await api.updateConstraint(id, editText.trim()).catch(() => {})
    setEditId(null)
    load()
  }

  function startEdit(item) {
    setEditId(item.id)
    setEditText(item.content)
  }

  return (
    <div className="card">
      <div className="card-title">농장 팩트</div>
      <p className="text-muted" style={{ marginBottom: 16 }}>
        AI가 제안 생성 전 반드시 참고하는 우리 농장의 사실 정보입니다.
        제안함에서 "사실과 다름"으로 거절하면 자동으로 추가됩니다.
      </p>

      {loading && <div className="text-muted" style={{ marginBottom: 12 }}>불러오는 중…</div>}

      {!loading && items.length === 0 && (
        <div className="text-muted" style={{ marginBottom: 16, fontSize: 13 }}>
          등록된 팩트가 없습니다.
        </div>
      )}

      {!loading && items.map(item => (
        <div key={item.id} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'center' }}>
          {editId === item.id ? (
            <>
              <input
                style={{ flex: 1, padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 13 }}
                value={editText}
                onChange={e => setEditText(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && saveEdit(item.id)}
                autoFocus
              />
              <button className="btn btn-primary" style={{ fontSize: 12 }} onClick={() => saveEdit(item.id)}>저장</button>
              <button className="btn btn-ghost" style={{ fontSize: 12 }} onClick={() => setEditId(null)}>취소</button>
            </>
          ) : (
            <>
              <span style={{ flex: 1, fontSize: 13 }}>{item.content}</span>
              <span className="text-muted" style={{ fontSize: 11, whiteSpace: 'nowrap' }}>
                {item.source === 'rejection' ? '거절에서 추가' : '직접 추가'}
              </span>
              <button className="btn btn-ghost" style={{ fontSize: 12 }} onClick={() => startEdit(item)}>수정</button>
              <button className="btn btn-danger" style={{ fontSize: 12 }} onClick={() => remove(item.id)}>삭제</button>
            </>
          )}
        </div>
      ))}

      <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
        <input
          ref={inputRef}
          style={{ flex: 1, padding: '7px 10px', border: '1px solid #ddd', borderRadius: 6, fontSize: 13 }}
          placeholder="예: 화학비료 사용 농가, 유기농 인증 없음"
          value={newText}
          onChange={e => setNewText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && add()}
        />
        <button className="btn btn-primary" onClick={add} disabled={!newText.trim()}>추가</button>
      </div>
    </div>
  )
}
