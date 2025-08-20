import { NextRequest, NextResponse } from "next/server";
import { ProgramStorage } from "@/lib/storage";
import { CreateProgramFormSchema } from "@/schemas/forms";

export async function GET(request: NextRequest) {
  try {
    ProgramStorage.initializeWithSampleData();

    const { searchParams } = new URL(request.url || "", "http://localhost");
    const sortBy = searchParams.get("sortBy") || "createdAt";
    const sortOrder = (searchParams.get("sortOrder") || "desc") as
      | "asc"
      | "desc";
    const page = parseInt(searchParams.get("page") || "1");
    const limit = parseInt(searchParams.get("limit") || "10");

    const validSortFields = ["name", "startDate", "eligibility", "createdAt"];
    if (!validSortFields.includes(sortBy)) {
      return NextResponse.json(
        {
          error: `Invalid sortBy field. Must be one of: ${validSortFields.join(", ")}`,
        },
        { status: 400 },
      );
    }

    if (!["asc", "desc"].includes(sortOrder)) {
      return NextResponse.json(
        { error: 'Invalid sortOrder. Must be "asc" or "desc"' },
        { status: 400 },
      );
    }

    if (page < 1) {
      return NextResponse.json(
        { error: "Page must be greater than 0" },
        { status: 400 },
      );
    }

    if (limit < 1 || limit > 100) {
      return NextResponse.json(
        { error: "Limit must be between 1 and 100" },
        { status: 400 },
      );
    }

    const result = ProgramStorage.getPaginatedPrograms({
      page,
      limit,
      sortBy,
      sortOrder,
    });

    return NextResponse.json(result);
  } catch (error) {
    console.error("Error fetching programs:", error);
    return NextResponse.json(
      { error: "Failed to fetch programs" },
      { status: 500 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const bodyWithDate = {
      ...body,
      startDate: body.startDate ? new Date(body.startDate) : undefined,
    };

    const validationResult = CreateProgramFormSchema.safeParse(bodyWithDate);

    if (!validationResult.success) {
      return NextResponse.json(
        {
          error: "Validation failed",
          details: validationResult.error.issues,
        },
        { status: 400 },
      );
    }

    const { name, startDate, website, twitter, type, identifier, description } =
      validationResult.data;

    const newProgram = ProgramStorage.addProgram({
      name,
      startDate: startDate.toISOString(),
      website: website || undefined,
      twitter: twitter || undefined,
      type,
      identifier,
      description: description || undefined,
      eligibility: "eligible",
    });

    return NextResponse.json({ program: newProgram }, { status: 201 });
  } catch (error) {
    console.error("Error creating program:", error);
    return NextResponse.json(
      { error: "Failed to create program" },
      { status: 500 },
    );
  }
}
