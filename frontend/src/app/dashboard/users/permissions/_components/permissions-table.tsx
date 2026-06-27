"use client"

import * as React from "react"
import { usePathname, useSearchParams, useRouter } from "next/navigation"
import { Search, Pencil, Trash2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { DataTablePagination } from "@/components/ui/data-table-pagination"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { ApiPermission } from "@/lib/types/roles"

function getCategory(code: string) {
  if (code === "*:*") return "System"
  const prefix = code.split(":")[0]
  return prefix.charAt(0).toUpperCase() + prefix.slice(1)
}

interface PermissionsTableProps {
  permissions: ApiPermission[]
  page: number
  pageSize: number
  total: number
  totalPages: number
  onEdit: (perm: ApiPermission) => void
  onDelete: (perm: ApiPermission) => void
}

export function PermissionsTable({
  permissions,
  page,
  pageSize,
  total,
  totalPages,
  onEdit,
  onDelete,
}: PermissionsTableProps) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [search, setSearch] = React.useState("")

  function handlePageChange(newPage: number) {
    const params = new URLSearchParams(searchParams.toString())
    params.set("page", String(newPage))
    params.set("page_size", String(pageSize))
    router.push(`${pathname}?${params}`)
  }

  function handlePageSizeChange(newSize: number) {
    const params = new URLSearchParams(searchParams.toString())
    params.set("page", "1")
    params.set("page_size", String(newSize))
    router.push(`${pathname}?${params}`)
  }

  const filtered = React.useMemo(() => {
    const q = search.toLowerCase()
    if (!q) return permissions
    return permissions.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.code.toLowerCase().includes(q) ||
        p.description?.toLowerCase().includes(q),
    )
  }, [permissions, search])

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-4">
          <div>
            <CardTitle className="text-base">All Permissions</CardTitle>
            <CardDescription>
              {total} permission{total !== 1 ? "s" : ""}
            </CardDescription>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Search permissions…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8"
            />
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0 pb-2">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="pl-6">Name</TableHead>
              <TableHead>Code</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Description</TableHead>
              <TableHead className="pr-6 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="py-10 text-center text-muted-foreground">
                  {search ? "No permissions match your search." : "No permissions yet."}
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((perm) => (
                <TableRow key={perm.id}>
                  <TableCell className="pl-6 font-medium">{perm.name}</TableCell>
                  <TableCell>
                    <code className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">
                      {perm.code}
                    </code>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">
                      {getCategory(perm.code)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm max-w-[260px] truncate">
                    {perm.description || "—"}
                  </TableCell>
                  <TableCell className="pr-6 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        aria-label="Edit permission"
                        onClick={() => onEdit(perm)}
                      >
                        <Pencil />
                      </Button>
                      <Button
                        variant="destructive"
                        size="icon-sm"
                        aria-label="Delete permission"
                        onClick={() => onDelete(perm)}
                      >
                        <Trash2 />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        <DataTablePagination
          page={page}
          pageSize={pageSize}
          total={total}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
        />
      </CardContent>
    </Card>
  )
}
