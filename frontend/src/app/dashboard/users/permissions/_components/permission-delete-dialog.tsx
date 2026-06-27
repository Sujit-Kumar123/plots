"use client"

import { DeleteDialog } from "@/components/ui/delete-dialog"
import { deletePermission } from "@/lib/services/server/permissions"
import type { ApiPermission } from "@/lib/types/roles"

interface PermissionDeleteDialogProps {
  permission: ApiPermission | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function PermissionDeleteDialog({
  permission,
  open,
  onOpenChange,
}: PermissionDeleteDialogProps) {
  return (
    <DeleteDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Delete permission?"
      description={permission && (
        <>
          <strong>{permission.name}</strong>{" "}
          (<code className="font-mono text-xs">{permission.code}</code>) will be
          permanently deleted. This will fail if it is currently assigned to any role.
        </>
      )}
      onConfirm={async () => {
        if (!permission) return {}
        return await deletePermission(permission.id)
      }}
      successMessage="Permission deleted"
    />
  )
}
