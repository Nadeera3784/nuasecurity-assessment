"use client";

import { useState, useEffect, memo, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ConfirmationDialog } from "@/components/ui/confirmation-dialog";
import { ProgramForm } from "@/components/program/program-form";
import { fetchPrograms, createProgram, deleteProgram } from "@/lib/intercom";
import Statistics from "@/components/program/statistics";
import { CreateProgramFormDataType } from "@/types";
import { ApiProgram, CreateProgramRequest, Program } from "@/interfaces";
import {
  Action,
  Column,
  DataTable,
  defaultRenderers,
} from "@/components/shared/data-table";
import { TrashIcon } from "lucide-react";
import { CustomPagination } from "@/components/shared/custom-pagination";

const MemoizedStatistics = memo(Statistics);

export default function ProgramPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [showDialog, setShowDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [sortConfig, setSortConfig] = useState<{
    field: keyof Program;
    order: "asc" | "desc";
  }>({
    field: "createdAt",
    order: "desc",
  });

  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    totalCount: 0,
    totalPages: 0,
    hasNextPage: false,
    hasPreviousPage: false,
  });

  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    programId: string | null;
    programName: string;
    isDeleting: boolean;
  }>({
    isOpen: false,
    programId: null,
    programName: "",
    isDeleting: false,
  });

  const convertApiProgram = (apiProgram: ApiProgram): Program => ({
    id: apiProgram.id,
    name: apiProgram.name,
    startDate: new Date(apiProgram.startDate),
    website: apiProgram.website,
    twitter: apiProgram.twitter,
    type: apiProgram.type,
    identifier: apiProgram.identifier,
    description: apiProgram.description,
    eligibility: apiProgram.eligibility,
    createdAt: new Date(apiProgram.createdAt),
  });

  const columns: Column<Program>[] = [
    {
      key: "name",
      label: "Program",
      sortable: true,
      className: "font-medium text-primary",
      render: (value) => defaultRenderers.truncate(value, 20),
    },
    {
      key: "startDate",
      label: "Start Date",
      sortable: true,
      render: (value) => defaultRenderers.date(value),
    },
    {
      key: "identifier",
      label: "Asset Identifier",
      className: "font-mono text-sm",
    },
    {
      key: "description",
      label: "Description",
      render: (value) => defaultRenderers.tooltip(value || "", 15),
    },
    {
      key: "eligibility",
      label: "Bounty Eligibility",
      sortable: true,
      render: (value) =>
        defaultRenderers.badge(value, {
          variant: {
            eligible: "bg-green-100 text-green-700",
            ineligible: "bg-red-100 text-red-700",
          },
        }),
    },
  ];

  const actions: Action<Program>[] = [
    {
      label: "Delete",
      icon: <TrashIcon className="h-4 w-4" />,
      onClick: (program) => handleDeleteRequest(program.id),
      variant: "destructive",
    },
  ];

  const loadPrograms = useCallback(
    async (
      sortBy?: keyof Program,
      sortOrder?: "asc" | "desc",
      page?: number,
      limit?: number,
    ) => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchPrograms(
          sortBy ? String(sortBy) : undefined,
          sortOrder,
          page,
          limit,
        );
        const convertedPrograms = response.programs.map(convertApiProgram);
        setPrograms(convertedPrograms);
        setPagination(response.pagination);
      } catch (err) {
        setError("Failed to load programs");
        console.error("Error loading programs:", err);
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const handleSort = useCallback(
    async (field: keyof Program, order: "asc" | "desc") => {
      setSortConfig({ field, order });
      setPagination((prev) => ({ ...prev, page: 1 }));
      await loadPrograms(field, order, 1, pagination.limit);
    },
    [loadPrograms, pagination.limit],
  );

  const handlePageChange = useCallback(
    async (newPage: number) => {
      setPagination((prev) => ({ ...prev, page: newPage }));
      await loadPrograms(
        sortConfig.field,
        sortConfig.order,
        newPage,
        pagination.limit,
      );
    },
    [loadPrograms, sortConfig, pagination.limit],
  );

  useEffect(() => {
    loadPrograms(
      sortConfig.field,
      sortConfig.order,
      pagination.page,
      pagination.limit,
    );
  }, [
    loadPrograms,
    sortConfig.field,
    sortConfig.order,
    pagination.page,
    pagination.limit,
  ]);

  const handleSubmit = useCallback(
    async (data: CreateProgramFormDataType) => {
      try {
        const programData: CreateProgramRequest = {
          name: data.name,
          startDate: data.startDate,
          website: data.website || undefined,
          twitter: data.twitter || undefined,
          type: data.type || undefined,
          identifier: data.identifier,
          description: data.description || undefined,
          relatedPrograms: data.relatedPrograms || [],
        };

        await createProgram(programData);
        setShowDialog(false);
        await loadPrograms(
          sortConfig.field,
          sortConfig.order,
          pagination.page,
          pagination.limit,
        );
      } catch (err) {
        console.error("Error creating program:", err);
        alert("Failed to create program. Please try again.");
      }
    },
    [loadPrograms, sortConfig, pagination],
  );

  const handleCancel = useCallback(() => {
    setShowDialog(false);
  }, []);

  const handleDeleteRequest = (programId: string) => {
    const program = programs.find((p) => p.id === programId);
    setDeleteConfirmation({
      isOpen: true,
      programId,
      programName: program?.name || "",
      isDeleting: false,
    });
  };

  const handleDeleteConfirm = useCallback(async () => {
    if (!deleteConfirmation.programId) return;

    try {
      setDeleteConfirmation((prev) => ({ ...prev, isDeleting: true }));
      await deleteProgram(deleteConfirmation.programId);
      setDeleteConfirmation({
        isOpen: false,
        programId: null,
        programName: "",
        isDeleting: false,
      });
      await loadPrograms(
        sortConfig.field,
        sortConfig.order,
        pagination.page,
        pagination.limit,
      );
    } catch (err) {
      console.error("Error deleting program:", err);
      alert("Failed to delete program. Please try again.");
      setDeleteConfirmation((prev) => ({ ...prev, isDeleting: false }));
    }
  }, [deleteConfirmation.programId, loadPrograms, sortConfig, pagination]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteConfirmation({
      isOpen: false,
      programId: null,
      programName: "",
      isDeleting: false,
    });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg">Loading programs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-destructive mb-4">{error}</p>
          <Button
            onClick={() =>
              loadPrograms(
                sortConfig.field,
                sortConfig.order,
                pagination.page,
                pagination.limit,
              )
            }
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-200">
      <div className="container mx-auto py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Programs</h1>
          </div>
        </div>
        <div className="mb-6">
          <h3 className="text-xl font-bold">Subscription Details</h3>
        </div>
        <div className="mb-6">
          <MemoizedStatistics setShowDialog={setShowDialog} />
        </div>
        <DataTable
          data={programs}
          columns={columns}
          actions={actions}
          onSort={handleSort}
          currentSort={sortConfig}
          title="All Programs"
          emptyMessage="No programs found."
          getRowKey={(program) => program.id}
        />
        <CustomPagination
          pagination={pagination}
          onPageChange={handlePageChange}
        />
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Program</DialogTitle>
            </DialogHeader>
            <ProgramForm onSubmit={handleSubmit} onCancel={handleCancel} />
          </DialogContent>
        </Dialog>

        <ConfirmationDialog
          open={deleteConfirmation.isOpen}
          onOpenChange={(open) => !open && handleDeleteCancel()}
          title="Are you sure?"
          description={`Are you sure you want to delete "${deleteConfirmation.programName}"? This action cannot be undone.`}
          confirmText="Delete"
          cancelText="Cancel"
          variant="destructive"
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
          loading={deleteConfirmation.isDeleting}
        />
      </div>
    </div>
  );
}
