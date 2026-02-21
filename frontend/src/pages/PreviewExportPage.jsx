import { useState } from 'react'
import { apiRequest } from '../api/client'

export default function PreviewExportPage() {
  const [message, setMessage] = useState('No export yet')

  const exportDoc = async () => {
    const draftId = localStorage.getItem('draftId')
    if (!draftId) return setMessage('No draft to export')

    const generated = await apiRequest('/documents/generate', {
      method: 'POST',
      body: JSON.stringify({ draft_id: Number(draftId) }),
    })

    const file = await apiRequest(`/documents/${generated.document_id}/file`)
    const url = URL.createObjectURL(file)
    const a = document.createElement('a')
    a.href = url
    a.download = generated.file_name
    a.click()
    URL.revokeObjectURL(url)
    setMessage(`Exported ${generated.file_name}`)
  }

  return (
    <section>
      <h2>Preview & Export</h2>
      <p>{message}</p>
      <button onClick={exportDoc}>Generate and Download</button>
    </section>
  )
}
