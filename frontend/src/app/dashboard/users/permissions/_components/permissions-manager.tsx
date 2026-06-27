"use client"

import * as React from "react"
import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { PermissionsTable } from "./permissions-table"
import { PermissionSheet } from "./permission-sheet"
import { PermissionDeleteDialog } from "./permission-delete-dialog"
import type { ApiPermission } from "@/lib/types/roles"

interface PermissionsManagerProps {
  permissions: ApiPermission[]
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export function PermissionsManager({ permissions, page, pageSize, total, totalPages }: PermissionsManagerProps) {
  const [sheetOpen, setSheetOpen] = React.useState(false)
  const [editingPerm, setEditingPerm] = React.useState<ApiPermission | null>(null)
  const [deletingPerm, setDeletingPerm] = React.useState<ApiPermission | null>(null)

  function openCreate() {
    setEditingPerm(null)
    setSheetOpen(true)
  }

  function openEdit(perm: ApiPermission) {
    setEditingPerm(perm)
    setSheetOpen(true)
  }

  function handleSheetOpenChange(open: boolean) {
    setSheetOpen(open)
    if (!open) setEditingPerm(null)
  }

  function handleDeleteOpenChange(open: boolean) {
    if (!open) setDeletingPerm(null)
  }

  return (
    <>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Permissions</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Define individual permissions that can be assigned to roles.
          </p>
        </div>
        <Button size="sm" onClick={openCreate}>
          <Plus />
          Add Permission
        </Button>
      </div>

      <PermissionsTable
        permissions={permissions}
        page={page}
        pageSize={pageSize}
        total={total}
        totalPages={totalPages}
        onEdit={openEdit}
        onDelete={setDeletingPerm}
      />

      <PermissionSheet
        open={sheetOpen}
        onOpenChange={handleSheetOpenChange}
        editingPerm={editingPerm}
      />

      <PermissionDeleteDialog
        permission={deletingPerm}
        open={!!deletingPerm}
        onOpenChange={handleDeleteOpenChange}
      />
    </>
  )
}
