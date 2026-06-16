import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { Badge } from '../components/Badge';

export const ProspectList: React.FC = () => {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useQuery({
    queryKey: ['prospects', page],
    queryFn: async () => (await fetch(`http://localhost:8000/api/v1/prospects?page=${page}`)).json()
  });

  if (isLoading || !data) return <div className="p-10 text-center">Chargement...</div>;

  return (
    <div className="space-y-6 p-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Prospects</h1>
        <a href="http://localhost:8000/api/v1/prospects/export/csv" className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
          <Download size={18} /> <span>Exporter CSV</span>
        </a>
      </div>
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ville</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {data.items.map((p: any) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap font-medium text-blue-600">{p.first_name} {p.last_name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{p.city}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold">{p.prospect_score}</td>
                <td className="px-6 py-4 whitespace-nowrap"><Badge type="tier" value={p.tier} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
