import {
  ApiProgram,
  CreateProgramRequest,
  PaginatedProgramsResponse,
} from "@/interfaces";

/*
 * TODO: Make this dynamic with URL and DTO
 */

export async function fetchPrograms(
  sortBy?: string,
  sortOrder?: "asc" | "desc",
  page?: number,
  limit?: number,
): Promise<PaginatedProgramsResponse> {
  const params = new URLSearchParams();
  if (sortBy) params.append("sortBy", sortBy);
  if (sortOrder) params.append("sortOrder", sortOrder);
  if (page) params.append("page", page.toString());
  if (limit) params.append("limit", limit.toString());

  const url = `/api/programs${params.toString() ? `?${params.toString()}` : ""}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch programs");
  }
  const data = await response.json();
  return data;
}

export async function createProgram(
  programData: CreateProgramRequest,
): Promise<ApiProgram> {
  const response = await fetch("/api/programs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...programData,
      startDate: programData.startDate.toISOString(),
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to create program");
  }

  const data = await response.json();
  return data.program;
}

export async function updateProgram(
  id: string,
  programData: CreateProgramRequest,
): Promise<ApiProgram> {
  const response = await fetch(`/api/programs/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...programData,
      startDate: programData.startDate.toISOString(),
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to update program");
  }

  const data = await response.json();
  return data.program;
}

export async function deleteProgram(id: string): Promise<void> {
  const response = await fetch(`/api/programs/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to delete program");
  }
}

export async function fetchProgram(id: string): Promise<ApiProgram> {
  const response = await fetch(`/api/programs/${id}`);
  if (!response.ok) {
    throw new Error("Failed to fetch program");
  }
  const data = await response.json();
  return data.program;
}
