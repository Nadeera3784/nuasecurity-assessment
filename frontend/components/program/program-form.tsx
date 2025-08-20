"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarIcon, PlusIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { CreateProgramFormSchema } from "@/schemas/forms";
import { CreateProgramFormType, CreateProgramFormDataType } from "@/types";
import { ASSET_TYPES } from "@/constants";
import { fetchPrograms } from "@/lib/intercom";
import { ApiProgram } from "@/interfaces";
import EligibilityTable from "./eligibility-table";

export function ProgramForm({ onSubmit, onCancel }: CreateProgramFormType) {
  const [open, setOpen] = useState(false);
  const [tempDate, setTempDate] = useState<Date | undefined>(undefined);
  const [availablePrograms, setAvailablePrograms] = useState<ApiProgram[]>([]);
  const [selectedProgramId, setSelectedProgramId] = useState<string>("");
  const [relatedPrograms, setRelatedPrograms] = useState<ApiProgram[]>([]);
  const [error, setError] = useState<string>("");

  const form = useForm<CreateProgramFormDataType>({
    resolver: zodResolver(CreateProgramFormSchema),
    defaultValues: {
      name: "",
      startDate: new Date(),
      website: "",
      twitter: "",
      type: undefined,
      identifier: "",
      description: "",
      relatedPrograms: undefined,
    },
  });

  useEffect(() => {
    const loadPrograms = async () => {
      try {
        const response = await fetchPrograms();
        setAvailablePrograms(response.programs);
      } catch (error) {
        console.error("Failed to load programs:", error);
      }
    };
    loadPrograms();
  }, []);

  const handleAddRelatedProgram = () => {
    setError("");

    if (!selectedProgramId) {
      setError("Please select a program");
      return;
    }

    const selectedProgram = availablePrograms.find(
      (p) => p.id === selectedProgramId,
    );
    if (!selectedProgram) {
      setError("Selected program not found");
      return;
    }

    if (relatedPrograms.some((p) => p.id === selectedProgramId)) {
      setError("This program is already added");
      return;
    }

    const newRelatedPrograms = [...relatedPrograms, selectedProgram];
    setRelatedPrograms(newRelatedPrograms);

    form.setValue(
      "relatedPrograms",
      newRelatedPrograms.map((p) => p.id),
    );

    setSelectedProgramId("");
  };

  const handleRemoveRelatedProgram = (programId: string) => {
    const newRelatedPrograms = relatedPrograms.filter(
      (p) => p.id !== programId,
    );
    setRelatedPrograms(newRelatedPrograms);

    form.setValue(
      "relatedPrograms",
      newRelatedPrograms.map((p) => p.id),
    );
  };

  const handleSubmit = (data: CreateProgramFormDataType) => {
    onSubmit(data);
  };

  return (
    <div className="space-y-6">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="mb-2">Program Name *</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter program name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="startDate"
              render={({ field }) => {
                return (
                  <FormItem className="mb-1">
                    <FormLabel>Start Date *</FormLabel>
                    <Popover open={open} onOpenChange={setOpen}>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            className={cn(
                              "w-full pl-3 text-left font-normal",
                              !field.value && "text-muted-foreground",
                            )}
                          >
                            {field.value ? (
                              format(field.value, "PPP")
                            ) : (
                              <span>Pick a date</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-full p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={tempDate}
                          onSelect={setTempDate}
                          disabled={(date) => {
                            const today = new Date();
                            today.setHours(0, 0, 0, 0);
                            return date < today;
                          }}
                          onCancel={() => {
                            setTempDate(field.value);
                            setOpen(false);
                          }}
                          onConfirm={() => {
                            if (tempDate) {
                              field.onChange(tempDate);
                            }
                            setOpen(false);
                          }}
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                );
              }}
            />
            <FormField
              control={form.control}
              name="website"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Website</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter your website" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="twitter"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Twitter/X</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter @username" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <FormField
            control={form.control}
            name="type"
            render={({ field }) => (
              <FormItem className="w-full">
                <FormLabel>Asset You Want to Test</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value ?? undefined}
                >
                  <FormControl>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Please select" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="max-h-64">
                    {ASSET_TYPES.map(({ value, label, icon: Icon }) => (
                      <SelectItem
                        key={value}
                        value={value}
                        className="cursor-pointer"
                      >
                        <div className="flex items-center gap-2">
                          <Icon className="h-4 w-4" />
                          <span>{label}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="identifier"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Asset Identifier</FormLabel>
                <FormControl>
                  <Input placeholder="Write your asset Identifier" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Description</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Description..."
                    className="min-h-16"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="space-y-4">
            <div>
              <FormLabel>Bounty Eligibility</FormLabel>
              <div className="flex gap-2 mt-2">
                <Select
                  value={selectedProgramId}
                  onValueChange={setSelectedProgramId}
                >
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="Please Select" />
                  </SelectTrigger>
                  <SelectContent className="max-h-64">
                    {availablePrograms.map((program) => (
                      <SelectItem
                        key={program.id}
                        value={program.id}
                        className="cursor-pointer"
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className={cn(
                              "px-2 py-1 rounded-full text-xs font-medium",
                              program.type === "web"
                                ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                                : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
                            )}
                          >
                            {program.type?.toUpperCase() || "N/A"}
                          </span>
                          <span>{program.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  onClick={handleAddRelatedProgram}
                  className="px-6 cursor-pointer"
                >
                  <PlusIcon className="h-4 w-4 mr-1" />
                  Add
                </Button>
              </div>
              {error && (
                <p className="text-sm text-destructive mt-1">{error}</p>
              )}
            </div>
            {relatedPrograms.length > 0 && (
              <EligibilityTable
                relatedPrograms={relatedPrograms}
                handleRemoveRelatedProgram={handleRemoveRelatedProgram}
              />
            )}
          </div>
          <div className="flex justify-between space-x-4">
            <Button
              type="button"
              className="w-1/2 text-primary bg-primary/10 cursor-pointer"
              variant="secondary"
              size="lg"
              onClick={onCancel}
            >
              Cancel
            </Button>
            <Button type="submit" className="w-1/2 cursor-pointer" size="lg">
              Submit
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
