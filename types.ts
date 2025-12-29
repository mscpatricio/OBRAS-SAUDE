
export enum WorkStatus {
  DELIVERED = 'Entregue',
  IN_PROGRESS = 'Em Andamento',
  PLANNED = 'Previsto',
  REVITALIZED = 'Revitalizado'
}

export interface BedBreakdown {
  category: string;
  count: number;
}

export interface Hospital {
  id: string;
  name: string;
  acronym: string;
  totalBeds2023?: number; // Kept for historical analysis if available
  totalBedsCurrent: number;
  icuBeds?: string; // e.g. "15", "02 - 30"
  operatingRooms?: number;
  plannedExpansion?: string; // e.g. "192", "31 L. (ITU)"
  bedBreakdown2023?: BedBreakdown[];
  bedBreakdownCurrent?: BedBreakdown[];
  works: Work[];
  notes?: string;
  analysis?: string; // Deep analysis text for the report
}

export interface Work {
  id: string;
  title: string;
  status: WorkStatus;
  description?: string;
  completionDate?: string;
  details?: string[];
}

export interface DashboardStats {
  totalBeds: number;
  bedsAdded: number;
  worksInProgress: number;
  worksDelivered: number;
  totalPlannedExpansion: number;
}
