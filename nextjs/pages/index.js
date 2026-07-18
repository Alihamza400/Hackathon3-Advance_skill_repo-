export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-primary text-white p-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold">LearnFlow</h1>
        <p className="mt-2 text-lg">AI-Powered Learning Platform</p>
        <a href="/dashboard" className="mt-4 inline-block bg-secondary text-white px-4 py-2 rounded-md hover:bg-blue-600 transition">
          Go to Dashboard
        </a>
      </div>
    </div>
  )
}