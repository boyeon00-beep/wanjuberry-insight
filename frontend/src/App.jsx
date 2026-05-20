import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Suggestions from './pages/Suggestions'
import ActionLogs from './pages/ActionLogs'
import AdReport from './pages/AdReport'
import Performance from './pages/Performance'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <div className="sidebar">
        <div className="sidebar-title">완주베리 인사이트</div>
        <NavLink to="/" end>대시보드</NavLink>
        <NavLink to="/analysis">분석</NavLink>
        <NavLink to="/suggestions">제안함</NavLink>
        <NavLink to="/ad-report">검색광고 보고서</NavLink>
        <NavLink to="/performance">성과 추적</NavLink>
        <NavLink to="/action-logs">실행 로그</NavLink>
        <NavLink to="/settings">설정</NavLink>
      </div>
      <div className="main">
        <Routes>
          <Route path="/"             element={<Dashboard />} />
          <Route path="/analysis"     element={<Analysis />} />
          <Route path="/suggestions"  element={<Suggestions />} />
          <Route path="/action-logs"  element={<ActionLogs />} />
          <Route path="/ad-report"    element={<AdReport />} />
          <Route path="/performance"  element={<Performance />} />
          <Route path="/settings"     element={<Settings />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
