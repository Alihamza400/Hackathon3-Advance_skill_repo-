import { useState, useEffect } from 'react';
import Card from '../components/Card';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState({
    courses: 5,
    agents: 3,
    users: 42,
  });

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data.status || 'Error'))
      .catch(() => setHealth('Error'));
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-primary mb-6">LearnFlow Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card title="Total Courses" value={stats.courses} />
        <Card title="Active Agents" value={stats.agents} />
        <Card title="Registered Users" value={stats.users} />
      </div>

      <div className="bg-white rounded-lg shadow-card p-4 flex flex-col h-full">
        <h2 className="text-secondary text-sm font-medium mb-2">Health Check</h2>
        <p className="text-lg font-medium">{health || 'Loading...'}</p>
      </div>
    </div>
  )
}