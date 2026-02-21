import { Link } from 'react-router-dom'

export default function Nav() {
  return (
    <nav style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
      <Link to="/">Selection</Link>
      <Link to="/interview">Interview</Link>
      <Link to="/outline">Clause Outline</Link>
      <Link to="/preview">Preview/Export</Link>
    </nav>
  )
}
