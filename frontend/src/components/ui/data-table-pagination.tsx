"use client"

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export interface DataTablePaginationProps {
  page: number
  pageSize: number
  total: number
  totalPages: number
  onPageChange: (page: number) => void
  onPageSizeChange: (size: number) => void
  pageSizeOptions?: number[]
}

export function DataTablePagination({
  page,
  pageSize,
  total,
  totalPages,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 25, 30, 50],
}: DataTablePaginationProps) {
  const canPrev = page > 1
  const canNext = page < totalPages
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1
  const to = Math.min(page * pageSize, total)

  return (
    <div className="flex items-center justify-between px-2 py-3">
      <p className="text-sm text-muted-foreground">
        {total === 0 ? "No results" : `${from}–${to} of ${total}`}
      </p>

      <div className="flex items-center gap-6">
        {/* Rows per page */}
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium max-sm:hidden">Rows per page</p>
          <Select
            value={String(pageSize)}
            onValueChange={(v) => onPageSizeChange(Number(v))}
          >
            <SelectTrigger className="h-8 w-[70px] cursor-pointer">
              <SelectValue />
            </SelectTrigger>
            <SelectContent side="top">
              {pageSizeOptions.map((size) => (
                <SelectItem key={size} value={String(size)} className="cursor-pointer">
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Page indicator */}
        <div className="flex w-24 items-center justify-center text-sm font-medium">
          Page {page} of {totalPages || 1}
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            className="hidden size-8 cursor-pointer lg:flex"
            onClick={() => onPageChange(1)}
            disabled={!canPrev}
            aria-label="First page"
          >
            <ChevronsLeft />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="size-8 cursor-pointer"
            onClick={() => onPageChange(page - 1)}
            disabled={!canPrev}
            aria-label="Previous page"
          >
            <ChevronLeft />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="size-8 cursor-pointer"
            onClick={() => onPageChange(page + 1)}
            disabled={!canNext}
            aria-label="Next page"
          >
            <ChevronRight />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="hidden size-8 cursor-pointer lg:flex"
            onClick={() => onPageChange(totalPages)}
            disabled={!canNext}
            aria-label="Last page"
          >
            <ChevronsRight />
          </Button>
        </div>
      </div>
    </div>
  )
}
