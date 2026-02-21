import { useEffect } from 'react'
import { apiRequest } from '../api/client'

export function useAutosaveDraft(draftId, draftState) {
  useEffect(() => {
    if (!draftId) return
    const handle = setTimeout(() => {
      apiRequest(`/drafts/${draftId}`, {
        method: 'PUT',
        body: JSON.stringify(draftState),
      }).catch(console.error)
    }, 800)

    return () => clearTimeout(handle)
  }, [draftId, draftState])
}
