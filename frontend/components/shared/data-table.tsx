"use client";

import { format } from "date-fns";
import { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { EllipsisVertical, ChevronUp, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => ReactNode; //eslint-disable-line
  className?: string;
  headerClassName?: string;
}

export interface Action<T> {
  label: string;
  icon: ReactNode;
  onClick: (item: T) => void;
  variant?: "default" | "destructive";
  show?: (item: T) => boolean;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  actions?: Action<T>[];
  onSort?: (sortBy: keyof T, sortOrder: "asc" | "desc") => void;
  currentSort?: { field: keyof T; order: "asc" | "desc" };
  pagination?: {
    page: number;
    limit: number;
    totalCount: number;
  };
  title?: string;
  emptyMessage?: string;
  className?: string;
  getRowKey?: (item: T) => string | number;
  rowClassName?: (item: T) => string;
}

const defaultRenderers = {
  date: (value: any) => {
    //eslint-disable-line
    if (!value) return "";
    const date = value instanceof Date ? value : new Date(value);
    return format(date, "MMM dd, yyyy");
  },

  truncate: (value: string, maxLength: number = 15) => {
    if (!value) return "";
    return value.length > maxLength ? `${value.slice(0, maxLength)}...` : value;
  },

  badge: (
    value: string,
    options: {
      variant: Record<string, string>;
      defaultVariant?: string;
    },
  ) => {
    const variant =
      options.variant[value] ||
      options.defaultVariant ||
      "bg-gray-100 text-gray-700";
    return (
      <span
        className={cn("px-2 py-1 rounded-full text-xs font-medium", variant)}
      >
        {value}
      </span>
    );
  },

  tooltip: (value: string, maxLength: number = 10) => {
    const truncated = defaultRenderers.truncate(value, maxLength);
    if (truncated === value) return value;

    return (
      <Tooltip>
        <TooltipTrigger>{truncated}</TooltipTrigger>
        <TooltipContent className="max-w-xs">
          <p>{value}</p>
        </TooltipContent>
      </Tooltip>
    );
  },
};

function DataTableRow<T extends Record<string, any>>({
  //eslint-disable-line
  item,
  columns,
  actions,
  getRowKey,
  rowClassName,
}: {
  item: T;
  columns: Column<T>[];
  actions?: Action<T>[];
  getRowKey?: (item: T) => string | number;
  rowClassName?: (item: T) => string;
}) {
  const rowKey = getRowKey ? getRowKey(item) : item.id || JSON.stringify(item);
  const className = rowClassName ? rowClassName(item) : "";

  return (
    <tr
      key={rowKey}
      className={cn("border-t border-gray-200 hover:bg-muted/25", className)}
    >
      {columns.map((column) => {
        const value = item[column.key];
        const renderedValue = column.render
          ? column.render(value, item)
          : value?.toString() || "";

        return (
          <td key={String(column.key)} className={cn("p-2", column.className)}>
            {renderedValue}
          </td>
        );
      })}

      {actions && actions.length > 0 && (
        <td className="p-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="data-[state=open]:bg-muted text-muted-foreground flex size-8 cursor-pointer"
                size="icon"
              >
                <EllipsisVertical />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-32">
              {actions
                .filter((action) => !action.show || action.show(item))
                .map((action, index) => (
                  <DropdownMenuItem
                    key={index}
                    variant={action.variant}
                    onClick={() => action.onClick(item)}
                  >
                    {action.icon}
                    {action.label}
                  </DropdownMenuItem>
                ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </td>
      )}
    </tr>
  );
}

export function DataTable<T extends Record<string, any>>( //eslint-disable-line
  props: DataTableProps<T>,
) {
  return <DataTableComponent {...props} />;
}

const DataTableHeader = <T extends Record<string, any>>({
  //eslint-disable-line
  columns,
  actions,
  onSort,
  currentSort, //eslint-disable-line
  getSortIcon,
  handleSort,
}: {
  columns: Column<T>[];
  actions?: Action<T>[];
  onSort?: (sortBy: keyof T, sortOrder: "asc" | "desc") => void;
  currentSort?: { field: keyof T; order: "asc" | "desc" };
  getSortIcon: (field: keyof T) => ReactNode;
  handleSort: (field: keyof T) => void;
}) => (
  <thead className="bg-muted/50">
    <tr>
      {columns.map((column) => (
        <th
          key={String(column.key)}
          className={cn("text-left p-2 font-medium", column.headerClassName)}
        >
          {column.sortable ? (
            <button
              onClick={() => handleSort(column.key)}
              className={cn(
                "flex items-center hover:text-primary transition-colors",
                onSort ? "cursor-pointer" : "cursor-default",
              )}
              disabled={!onSort}
            >
              {column.label}
              {getSortIcon(column.key)}
            </button>
          ) : (
            column.label
          )}
        </th>
      ))}
      {actions && actions.length > 0 && (
        <th className="text-left p-2 font-medium"></th>
      )}
    </tr>
  </thead>
);

function DataTableComponent<T extends Record<string, any>>({
  //eslint-disable-line
  data,
  columns,
  actions,
  onSort,
  currentSort,
  pagination,
  title,
  emptyMessage = "No data available.",
  className,
  getRowKey,
  rowClassName,
}: DataTableProps<T>) {
  const handleSort = (field: keyof T) => {
    if (!onSort) return;

    const newOrder =
      currentSort?.field === field && currentSort?.order === "asc"
        ? "desc"
        : "asc";
    onSort(field, newOrder);
  };

  const getSortIcon = (field: keyof T) => {
    if (!currentSort || currentSort.field !== field) {
      return null;
    }
    return currentSort.order === "asc" ? (
      <ChevronUp className="h-4 w-4 ml-1 inline" />
    ) : (
      <ChevronDown className="h-4 w-4 ml-1 inline" />
    );
  };

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      <div className="space-y-2">
        {title && <h3 className="text-xl font-bold">{title}</h3>}
        {pagination && (
          <p className="text-sm text-muted-foreground">
            Showing {(pagination.page - 1) * pagination.limit + 1} to{" "}
            {Math.min(
              pagination.page * pagination.limit,
              pagination.totalCount,
            )}{" "}
            of {pagination.totalCount} items
          </p>
        )}
      </div>

      <div className="bg-white rounded-lg overflow-hidden">
        <table className="w-full">
          <DataTableHeader
            columns={columns}
            actions={actions}
            onSort={onSort}
            currentSort={currentSort}
            getSortIcon={getSortIcon}
            handleSort={handleSort}
          />
          <tbody>
            {data.map((item) => (
              <DataTableRow
                key={
                  getRowKey ? getRowKey(item) : item.id || JSON.stringify(item)
                }
                item={item}
                columns={columns}
                actions={actions}
                getRowKey={getRowKey}
                rowClassName={rowClassName}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export { defaultRenderers };
