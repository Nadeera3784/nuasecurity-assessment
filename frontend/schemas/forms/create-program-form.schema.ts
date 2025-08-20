import z from "zod";

export const CreateProgramFormSchema = z.object({
  name: z
    .string()
    .min(1, "Program name is required")
    .max(50, "Name must be less than 50 characters"),
  startDate: z.date(),
  website: z
    .string()
    .optional()
    .refine(
      (v) =>
        !v ||
        v === "" ||
        (() => {
          try {
            new URL(v);
            return true;
          } catch {
            return false;
          }
        })(),
      { message: "Please enter a valid URL" },
    ),
  twitter: z
    .string()
    .optional()
    .refine((v) => !v || v === "" || /^@?[A-Za-z0-9_]{1,15}$/.test(v), {
      message: "Enter a valid handle (e.g. @username)",
    }),
  type: z.enum(["web", "mobile"]).optional(),
  identifier: z.string().min(1, "Asset identifier is required"),
  description: z
    .string()
    .max(100, "Description must be less than 100 characters")
    .optional(),
  relatedPrograms: z.array(z.string()).optional(),
});
