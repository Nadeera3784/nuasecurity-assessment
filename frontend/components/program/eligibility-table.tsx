import { Globe, Smartphone, Trash2Icon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn, truncate } from "@/lib/utils";
import { RelatedProgramsTableProps } from "@/interfaces";

const EligibilityTable: React.FC<RelatedProgramsTableProps> = ({
  relatedPrograms,
  handleRemoveRelatedProgram,
}) => {
  return (
    <div className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-muted/25">
            <tr>
              <th className="text-left p-3 font-medium text-sm">Type</th>
              <th className="text-left p-3 font-medium text-sm">
                Asset Identifier
              </th>
              <th className="text-left p-3 font-medium text-sm">Description</th>
              <th className="text-left p-3 font-medium text-sm">Eligibility</th>
              <th className="text-left p-3 font-medium text-sm"></th>
            </tr>
          </thead>
          <tbody>
            {relatedPrograms.map((program) => (
              <tr key={program.id} className="border-t hover:bg-muted/25">
                <td className="p-3">
                  {program.type === "web" ? (
                    <Globe className="h-4 w-4" />
                  ) : (
                    <Smartphone className="h-4 w-4" />
                  )}
                </td>
                <td className="p-3 font-mono text-sm truncate">
                  {truncate(program.identifier, 10)}
                </td>
                <td className="p-3 text-sm">
                  {program.description ? (
                    <span className="line-clamp-2 text-sm truncate">
                      {truncate(program.description, 10)}
                    </span>
                  ) : (
                    <span className="text-muted-foreground text-sm">N/A</span>
                  )}
                </td>
                <td className="p-3">
                  <span
                    className={cn(
                      "px-2 py-1 rounded-full text-xs font-medium",
                      program.eligibility === "eligible"
                        ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                        : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
                    )}
                  >
                    {program.eligibility === "eligible"
                      ? "Eligible"
                      : "Ineligible"}
                  </span>
                </td>
                <td className="p-3">
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    className="cursor-pointer"
                    onClick={() => handleRemoveRelatedProgram(program.id)}
                  >
                    <Trash2Icon className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EligibilityTable;
