export interface Program {
  id: string;
  name: string;
  startDate: Date;
  website?: string;
  twitter?: string;
  type?: "web" | "mobile";
  identifier: string;
  description?: string;
  eligibility: "eligible" | "ineligible";
  createdAt: Date;
}

export interface ApiProgram {
  id: string;
  name: string;
  startDate: string;
  website?: string;
  twitter?: string;
  type?: "web" | "mobile";
  identifier: string;
  description?: string;
  eligibility: "eligible" | "ineligible";
  createdAt: string;
  updatedAt: string;
}

export interface CreateProgramRequest {
  name: string;
  startDate: Date;
  website?: string;
  twitter?: string;
  type?: "web" | "mobile";
  identifier: string;
  description?: string;
  relatedPrograms?: string[];
}

export interface PaginatedProgramsResponse {
  programs: ApiProgram[];
  pagination: {
    page: number;
    limit: number;
    totalCount: number;
    totalPages: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
}

export interface ProgramListProps {
  programs: Program[];
  onEdit?: (program: Program) => void;
  onDelete?: (programId: string) => void;
  onSort?: (sortBy: string, sortOrder: "asc" | "desc") => void;
  currentSort?: {
    field: string;
    order: "asc" | "desc";
  };
  pagination?: {
    page: number;
    limit: number;
    totalCount: number;
    totalPages: number;
  };
}

export interface StatisticsProps {
  setShowDialog: React.Dispatch<React.SetStateAction<boolean>>;
}

export interface RelatedProgramsTableProps {
  relatedPrograms: ApiProgram[];
  handleRemoveRelatedProgram: (id: string) => void;
}
