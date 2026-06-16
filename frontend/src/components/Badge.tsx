import React from 'react';
const TIER_COLORS: Record<string, string> = { ambassador: 'bg-purple-100 text-purple-800 border-purple-200', champion: 'bg-blue-100 text-blue-800 border-blue-200', early_adopter: 'bg-green-100 text-green-800 border-green-200', standard: 'bg-gray-100 text-gray-800 border-gray-200' };
export const Badge: React.FC<{ type: 'tier' | 'status', value: string }> = ({ value }) => {
  const colorClass = TIER_COLORS[value] || 'bg-gray-100 text-gray-800';
  return <span className={`px-2 py-0.5 rounded text-xs font-bold ${colorClass}`}>{value.toUpperCase()}</span>;
};
