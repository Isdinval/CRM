export type Tier = 'ambassador' | 'champion' | 'early_adopter' | 'standard';
export interface Prospect { id: string; first_name: string; last_name: string; email: string; city: string; region: string; department: string; practice_name: string; practice_type: string; prospect_score: number; tier: Tier; }
