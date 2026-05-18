import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Suggestions from './pages/Suggestions'
import ActionLogs from './pages/ActionLogs'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <div className="sidebar">
        <div className="sidebar-title">완주베리 인사이트</div>
        <NavLink to="/" end>대시보드</NavLink>
        <NavLink to="/analysis">분석</NavLink>
        <NavLink to="/suggestions">제안함</NavLink>
        <NavLink to="/action-logs">실행 로그</NavLink>
        <NavLink to="/settings">설정</NavLink>
      </div>
      <div className="main">
        <Routes>
          <Route path="/"             element={<Dashboard />} />
          <Route path="/analysis"     element={<Analysis />} />
          <Route path="/suggestions"  element={<Suggestions />} />
          <Route path="/action-logs"  element={<ActionLogs />} />
          <Route path="/settings"     element={<Settings />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
