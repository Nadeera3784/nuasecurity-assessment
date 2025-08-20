import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

const CustomPagination = ({
  pagination,
  onPageChange,
}: {
  pagination: {
    page: number;
    totalPages: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
  onPageChange: (page: number) => void;
}) => {
  if (pagination.totalPages <= 1) return null;

  const generatePageNumbers = () => {
    const pages = [];
    const { page, totalPages } = pagination;

    pages.push(1);

    let startPage = Math.max(2, page - 1); //eslint-disable-line
    let endPage = Math.min(totalPages - 1, page + 1); //eslint-disable-line

    if (startPage > 2) {
      pages.push("ellipsis-start");
    }

    for (let i = startPage; i <= endPage; i++) {
      if (i !== 1 && i !== totalPages) {
        pages.push(i);
      }
    }

    if (endPage < totalPages - 1) {
      pages.push("ellipsis-end");
    }

    if (totalPages > 1) {
      pages.push(totalPages);
    }

    return pages;
  };

  const pageNumbers = generatePageNumbers();

  return (
    <div className="flex justify-center mt-6">
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() =>
                pagination.hasPreviousPage && onPageChange(pagination.page - 1)
              }
              className={
                pagination.hasPreviousPage
                  ? "cursor-pointer"
                  : "pointer-events-none opacity-50"
              }
            />
          </PaginationItem>

          {pageNumbers.map((pageNum, index) => (
            <PaginationItem key={index}>
              {pageNum === "ellipsis-start" || pageNum === "ellipsis-end" ? (
                <PaginationEllipsis />
              ) : (
                <PaginationLink
                  onClick={() => onPageChange(pageNum as number)}
                  isActive={pageNum === pagination.page}
                  className="cursor-pointer"
                >
                  {pageNum}
                </PaginationLink>
              )}
            </PaginationItem>
          ))}

          <PaginationItem>
            <PaginationNext
              onClick={() =>
                pagination.hasNextPage && onPageChange(pagination.page + 1)
              }
              className={
                pagination.hasNextPage
                  ? "cursor-pointer"
                  : "pointer-events-none opacity-50"
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

CustomPagination.displayName = "CustomPagination";

export { CustomPagination };
