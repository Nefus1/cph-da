import { useEffect, useState } from 'react'
import { apiRequest } from '../api/client'
import { useAutosaveDraft } from '../hooks/useAutosaveDraft'

export default function InterviewFlowPage() {
  const [draftId, setDraftId] = useState(localStorage.getItem('draftId'))
  const [answers, setAnswers] = useState('{}')
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    if (draftId) return
    apiRequest('/drafts/resume/latest')
      .then((data) => {
        setDraftId(String(data.draft_id))
        localStorage.setItem('draftId', String(data.draft_id))
      })
      .catch(() => {})
  }, [draftId])

  useAutosaveDraft(draftId, { answers_json: answers, current_step: currentStep, status: 'in_progress' })

  return (
    <section>
      <h2>Interview Flow</h2>
      <p>Draft: {draftId ?? 'none'}</p>
      <textarea value={answers} onChange={(e) => setAnswers(e.target.value)} rows={8} cols={60} />
      <div>
        <button onClick={() => setCurrentStep((v) => Math.max(0, v - 1))}>Back</button>
        <button onClick={() => setCurrentStep((v) => v + 1)}>Next</button>
      </div>
      <p>Current step: {currentStep}</p>
    </section>
  )
}
