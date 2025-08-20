import { CreateProgramFormSchema } from "@/schemas/forms";
import z from "zod";

export type CreateProgramFormDataType = z.infer<typeof CreateProgramFormSchema>;

export type CreateProgramFormType = {
  onSubmit: (data: CreateProgramFormDataType) => void;
  onCancel?: () => void;
};
