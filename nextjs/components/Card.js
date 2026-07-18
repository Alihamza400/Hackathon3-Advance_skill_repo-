export default function Card({title, value, children}) {
  return (
    <div className="bg-white rounded-lg shadow-card p-4 flex flex-col h-full">
      <h2 className="text-primary text-sm font-medium">{title}</h2>
      <p className="mt-1 text-lg font-medium">{value}</p>
      {children}
    </div>
  )
}