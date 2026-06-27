"use client"

import { useState, useTransition, useCallback } from "react"
import Link from "next/link"
import { useRouter, usePathname, useSearchParams } from "next/navigation"
import { ExternalLink, LayoutTemplate, Search, Trash2, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { DeleteDialog } from "@/components/ui/delete-dialog"
import { DataTablePagination } from "@/components/ui/data-table-pagination"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { deleteSheetAction } from "@/lib/services/server/sheets"
import type { PaginatedSheets, SheetListItem } from "@/lib/services/plot-sheets"

// ── Skeleton ──────────────────────────────────────────────────────────────────

function SheetCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="mt-1 h-3 w-1/2" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-5 w-20" />
      </CardContent>
      <CardFooter>
        <Skeleton className="h-8 w-full" />
      </CardFooter>
    </Card>
  )
}

export function SheetsGridSkeleton({ pageSize = 12 }: { pageSize?: number }) {
  return (
    <div className="flex flex-col gap-4">
      <Skeleton className="h-9 w-72" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: Math.min(pageSize, 12) }).map((_, i) => (
          <SheetCardSkeleton key={i} />
        ))}
      </div>
    </div>
  )
}

// ── Single card ───────────────────────────────────────────────────────────────

function SheetCard({ sheet }: { sheet: SheetListItem }) {
  const router = useRouter()
  const [deleteOpen, setDeleteOpen] = useState(false)

  return (
    <>
      <Card className="hover:ring-primary/30 transition-all">
        <CardHeader>
          <CardTitle className="truncate">{sheet.name || "Untitled Sheet"}</CardTitle>
          <CardDescription>
            Updated{" "}
            {new Date(sheet.updated_at).toLocaleDateString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
            })}
          </CardDescription>
          <CardAction>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-7 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                    onClick={() => setDeleteOpen(true)}
                  >
                    <Trash2 className="size-3.5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Delete sheet</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardAction>
        </CardHeader>

        <CardContent>
          <Badge variant="secondary">
            {sheet.sheet_w} × {sheet.sheet_d} units
          </Badge>
        </CardContent>

        <CardFooter>
          <Button asChild size="sm" className="w-full">
            <Link href={`/plot?sheet=${sheet.id}`}>
              <ExternalLink className="size-3.5" />
              Open Sheet
            </Link>
          </Button>
        </CardFooter>
      </Card>

      <DeleteDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete sheet?"
        description={`"${sheet.name || "Untitled Sheet"}" will be permanently deleted.`}
        onConfirm={async () => {
          const result = await deleteSheetAction(sheet.id)
          if (!result.error) router.refresh()
          return result
        }}
        successMessage="Sheet deleted"
      />
    </>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────

function EmptyState({ filtered }: { filtered: boolean }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <div className="flex size-14 items-center justify-center rounded-xl bg-muted">
        <LayoutTemplate className="size-6 text-muted-foreground" />
      </div>
      <div className="flex flex-col gap-1">
        <p className="text-sm font-medium">
          {filtered ? "No sheets match your search" : "No sheets yet"}
        </p>
        <p className="text-xs text-muted-foreground">
          {filtered
            ? "Try a different search term."
            : "Start drawing to save your first sheet."}
        </p>
      </div>
      {!filtered && (
        <>
          <Separator className="max-w-xs" />
          <Button asChild variant="outline" size="sm">
            <Link href="/plot">Create your first sheet</Link>
          </Button>
        </>
      )}
    </div>
  )
}

// ── Main grid ─────────────────────────────────────────────────────────────────

interface SheetsGridProps {
  data: PaginatedSheets
  search: string
}

export function SheetsGrid({ data, search }: SheetsGridProps) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [, startTransition] = useTransition()
  const [searchValue, setSearchValue] = useState(search)

  const updateParams = useCallback(
    (updates: Record<string, string | undefined>) => {
      const params = new URLSearchParams(searchParams.toString())
      for (const [key, value] of Object.entries(updates)) {
        if (value === undefined || value === "") {
          params.delete(key)
        } else {
          params.set(key, value)
        }
      }
      startTransition(() => {
        router.push(`${pathname}?${params.toString()}`)
      })
    },
    [pathname, router, searchParams],
  )

  function handleSearch(value: string) {
    setSearchValue(value)
    updateParams({ search: value || undefined, page: "1" })
  }

  function handlePageChange(page: number) {
    updateParams({ page: String(page) })
  }

  function handlePageSizeChange(size: number) {
    updateParams({ page_size: String(size), page: "1" })
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Search bar */}
      <div className="relative w-full max-w-sm">
        <Search className="absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search sheets…"
          value={searchValue}
          onChange={(e) => handleSearch(e.target.value)}
          className="pl-8 pr-8"
        />
        {searchValue && (
          <button
            onClick={() => handleSearch("")}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="size-3.5" />
          </button>
        )}
      </div>

      {/* Grid */}
      {data.items.length === 0 ? (
        <EmptyState filtered={!!searchValue} />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {data.items.map((s) => (
            <SheetCard key={s.id} sheet={s} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {data.total > 0 && (
        <>
          <Separator />
          <DataTablePagination
            page={data.page}
            pageSize={data.page_size}
            total={data.total}
            totalPages={data.total_pages}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
            pageSizeOptions={[6, 12, 24, 48]}
          />
        </>
      )}
    </div>
  )
}
