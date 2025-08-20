import { ApiProgram } from "@/interfaces/program.interface";

const STORAGE_KEY = "programs_data";

export class ProgramStorage {
  private static memoryStorage: ApiProgram[] = [];
  private static isClient = typeof window !== "undefined";
  static getPrograms(): ApiProgram[] {
    if (this.isClient) {
      try {
        const data = localStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : [];
      } catch (error) {
        console.warn(
          "Failed to read from localStorage, using memory storage:",
          error,
        );
        return this.memoryStorage;
      }
    }
    return this.memoryStorage;
  }

  static savePrograms(programs: ApiProgram[]): void {
    this.memoryStorage = programs;

    if (this.isClient) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(programs));
      } catch (error) {
        console.warn("Failed to save to localStorage:", error);
      }
    }
  }

  static addProgram(
    program: Omit<ApiProgram, "id" | "createdAt" | "updatedAt">,
  ): ApiProgram {
    const now = new Date().toISOString();
    const newProgram: ApiProgram = {
      ...program,
      id: this.generateId(),
      createdAt: now,
      updatedAt: now,
    };

    const programs = this.getPrograms();
    programs.push(newProgram);
    this.savePrograms(programs);

    return newProgram;
  }

  static getProgramById(id: string): ApiProgram | null {
    const programs = this.getPrograms();
    return programs.find((program) => program.id === id) || null;
  }

  static updateProgram(
    id: string,
    updates: Partial<Omit<ApiProgram, "id" | "createdAt">>,
  ): ApiProgram | null {
    const programs = this.getPrograms();
    const index = programs.findIndex((program) => program.id === id);

    if (index === -1) return null;

    const updatedProgram: ApiProgram = {
      ...programs[index],
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    programs[index] = updatedProgram;
    this.savePrograms(programs);

    return updatedProgram;
  }

  static deleteProgram(id: string): boolean {
    const programs = this.getPrograms();
    const index = programs.findIndex((program) => program.id === id);

    if (index === -1) return false;

    programs.splice(index, 1);
    this.savePrograms(programs);

    return true;
  }

  static getPaginatedPrograms(options: {
    page: number;
    limit: number;
    sortBy?: string;
    sortOrder?: "asc" | "desc";
  }) {
    const { page, limit, sortBy = "createdAt", sortOrder = "desc" } = options;
    const programs = this.getPrograms();

    const sortedPrograms = [...programs].sort((a, b) => {
      let aValue: string | Date, bValue: string | Date;

      switch (sortBy) {
        case "name":
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case "startDate":
          aValue = new Date(a.startDate);
          bValue = new Date(b.startDate);
          break;
        case "eligibility":
          aValue = a.eligibility;
          bValue = b.eligibility;
          break;
        case "createdAt":
        default:
          aValue = new Date(a.createdAt);
          bValue = new Date(b.createdAt);
          break;
      }

      if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    const totalCount = sortedPrograms.length;
    const totalPages = Math.ceil(totalCount / limit);
    const offset = (page - 1) * limit;
    const paginatedPrograms = sortedPrograms.slice(offset, offset + limit);

    return {
      programs: paginatedPrograms,
      pagination: {
        page,
        limit,
        totalCount,
        totalPages,
        hasNextPage: page < totalPages,
        hasPreviousPage: page > 1,
      },
    };
  }

  static initializeWithSampleData(): void {
    const programs = this.getPrograms();

    if (programs.length === 0) {
      const samplePrograms: ApiProgram[] = [
        {
          id: this.generateId(),
          name: "Sample Web Application",
          startDate: "2024-01-15T00:00:00.000Z",
          website: "https://example.com",
          twitter: "@example",
          type: "web",
          identifier: "web-app-001",
          description: "A sample web application for testing",
          eligibility: "eligible",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: this.generateId(),
          name: "Mobile App Test",
          startDate: "2024-02-01T00:00:00.000Z",
          website: "https://mobileapp.example.com",
          twitter: "@mobileapp",
          type: "mobile",
          identifier: "mobile-app-001",
          description: "A sample mobile application",
          eligibility: "ineligible",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: this.generateId(),
          name: "Citi’s Responsible Vulnerability",
          startDate: "2024-03-01T00:00:00.000Z",
          website: "https://hackerone.com/citi_group?type=team",
          twitter: "@mobileapp",
          type: "web",
          identifier: "citi-app-001",
          description: "The security of customer account information",
          eligibility: "ineligible",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];

      this.savePrograms(samplePrograms);
    }
  }

  private static generateId(): string {
    return `prog_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static clearAll(): void {
    this.memoryStorage = [];
    if (this.isClient) {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (error) {
        console.warn("Failed to clear localStorage:", error);
      }
    }
  }
}
