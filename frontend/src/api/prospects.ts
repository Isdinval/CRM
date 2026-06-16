const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/v1';
export const fetchProspects = async (p: any) => (await fetch(`${BASE}/prospects`)).json();
