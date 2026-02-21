const groups = [
  { name: 'Rules', items: ['Payment terms', 'Term and termination'] },
  { name: 'Standard', items: ['Governing law', 'Notices'] },
  { name: 'Optional', items: ['Non-solicit', 'Arbitration'] },
]

export default function ClauseOutlinePage() {
  return (
    <section>
      <h2>Clause Outline</h2>
      {groups.map((group) => (
        <div key={group.name}>
          <h3>{group.name}</h3>
          <ul>
            {group.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  )
}
