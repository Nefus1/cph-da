import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Nav from './components/Nav'
import ClauseOutlinePage from './pages/ClauseOutlinePage'
import DocumentSelectionPage from './pages/DocumentSelectionPage'
import InterviewFlowPage from './pages/InterviewFlowPage'
import PreviewExportPage from './pages/PreviewExportPage'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ fontFamily: 'sans-serif', padding: 20 }}>
        <h1>Contract Platform</h1>
        <Nav />
        <Routes>
          <Route path="/" element={<DocumentSelectionPage />} />
          <Route path="/interview" element={<InterviewFlowPage />} />
          <Route path="/outline" element={<ClauseOutlinePage />} />
          <Route path="/preview" element={<PreviewExportPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
