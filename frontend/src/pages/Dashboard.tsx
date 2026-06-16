import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Users, Star, MessageSquare, TrendingUp } from 'lucide-react';

const fetchStats = async () => {
  const res = await fetch('http://localhost:8000/api/v1/dashboard/stats');
  return res.json();
};

export const Dashboard: React.FC = () => {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard-stats'], queryFn: fetchStats });
  if (isLoading || !data) return <div className="p-10 text-center">Chargement...</div>;
  const kpis = [
    { title: 'Total Prospects', value: data.total, icon: Users, color: 'text-blue-600' },
    { title: 'Ambassadeurs', value: data.by_tier.ambassador, icon: Star, color: 'text-purple-600' },
    { title: 'Champions', value: data.by_tier.champion, icon: TrendingUp, color: 'text-indigo-600' },
    { title: 'Score Moyen', value: data.avg_score.toFixed(1), icon: MessageSquare, color: 'text-green-600' },
  ];
  return (
    <div className="space-y-8 p-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {kpis.map((kpi) => (
          <div key={kpi.title} className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center justify-between mb-2">
              <kpi.icon className={kpi.color} size={24} />
              <span className="text-2xl font-bold">{kpi.value}</span>
            </div>
            <p className="text-gray-500 text-sm font-medium">{kpi.title}</p>
          </div>
        ))}
      </div>
      <div className="bg-white p-6 rounded-xl shadow-sm border h-80">
        <h3 className="text-lg font-semibold mb-6">Répartition par Région</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.by_region}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="region" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
