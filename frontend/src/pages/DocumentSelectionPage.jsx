import { useState } from 'react'
import { apiRequest } from '../api/client'

export default function DocumentSelectionPage() {
  const [email, setEmail] = useState('demo@example.com')
  const [password, setPassword] = useState('password123')
  const [templateName, setTemplateName] = useState('Mutual NDA')

  const registerAndSeed = async () => {
    try {
      const auth = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('token', auth.access_token)
    } catch {
      const auth = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('token', auth.access_token)
    }

    const template = await apiRequest('/templates', {
      method: 'POST',
      body: JSON.stringify({ name: templateName, description: 'Generated from selection page' }),
    })

    const version = await apiRequest('/template-versions', {
      method: 'POST',
      body: JSON.stringify({ template_id: template.id, title: 'v1', body: 'Default template body' }),
    })

    const draft = await apiRequest('/drafts', {
      method: 'POST',
      body: JSON.stringify({ template_version_id: version.id }),
    })
    localStorage.setItem('draftId', String(draft.id))
    alert(`Draft ${draft.id} created.`)
  }

  return (
    <section>
      <h2>Document Selection</h2>
      <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
      <input value={templateName} onChange={(e) => setTemplateName(e.target.value)} placeholder="Template name" />
      <button onClick={registerAndSeed}>Start Draft</button>
    </section>
  )
}
