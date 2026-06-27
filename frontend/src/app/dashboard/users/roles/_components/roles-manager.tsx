"use client"

import * as React from "react"
import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  SheetClose,
} from "@/components/ui/sheet"
import { DeleteDialog } from "@/components/ui/delete-dialog"
import { RoleCard } from "./role-card"
import { createRole, updateRole, deleteRole } from "@/lib/services/server/roles"
import { toast } from "sonner"
import { Spinner } from "@/components/ui/spinner"
import type { ApiRole } from "@/lib/types/roles"

interface RolesManagerProps {
  roles: ApiRole[]
}

const EMPTY_FORM = { name: "", short_name: "", description: "" }

export function RolesManager({ roles }: RolesManagerProps) {
  const [sheetOpen, setSheetOpen] = React.useState(false)
  const [editingRole, setEditingRole] = React.useState<ApiRole | null>(null)
  const [form, setForm] = React.useState(EMPTY_FORM)
  const [saving, setSaving] = React.useState(false)
  const [saveError, setSaveError] = React.useState<string | null>(null)

  const [deletingRole, setDeletingRole] = React.useState<ApiRole | null>(null)

  function openCreate() {
    setEditingRole(null)
    setForm(EMPTY_FORM)
    setSaveError(null)
    setSheetOpen(true)
  }

  function openEdit(role: ApiRole) {
    setEditingRole(role)
    setForm({
      name: role.name,
      short_name: role.short_name,
      description: role.description ?? "",
    })
    setSaveError(null)
    setSheetOpen(true)
  }

  function setField(key: keyof typeof EMPTY_FORM, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSave() {
    setSaving(true)
    setSaveError(null)

    const result = editingRole
      ? await updateRole(editingRole.id, {
          name: form.name,
          short_name: form.short_name,
          description: form.description || undefined,
        })
      : await createRole({
          name: form.name,
          short_name: form.short_name,
          description: form.description || undefined,
        })

    setSaving(false)

    if (result.error) {
      setSaveError(result.error)
      toast.error(result.error)
      return
    }

    setSheetOpen(false)
    toast.success(editingRole ? "Role updated" : "Role created")
  }

  return (
    <>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Roles &amp; Permissions</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Define what each role can access across the application.
          </p>
        </div>
        <Button onClick={openCreate}>
          <Plus />
          Create Role
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {roles.map((role) => (
          <RoleCard
            key={role.id}
            role={role}
            onEdit={openEdit}
            onDelete={setDeletingRole}
          />
        ))}
      </div>

      {/* Create / Edit Sheet */}
      <Sheet open={sheetOpen} onOpenChange={(open) => { if (!open) setSheetOpen(false) }}>
        <SheetContent side="right">
          <SheetHeader>
            <SheetTitle>{editingRole ? "Edit Role" : "Create Role"}</SheetTitle>
            <SheetDescription>
              {editingRole
                ? `Update details for the "${editingRole.name}" role.`
                : "Add a new role to the system."}
            </SheetDescription>
          </SheetHeader>

          <div className="flex flex-col gap-5 px-4 py-2">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="role-name">Name</Label>
              <Input
                id="role-name"
                placeholder="e.g. Editor"
                value={form.name}
                onChange={(e) => setField("name", e.target.value)}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="role-short-name">Short name</Label>
              <Input
                id="role-short-name"
                placeholder="e.g. editor"
                value={form.short_name}
                onChange={(e) => setField("short_name", e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Lowercase identifier used internally (no spaces).
              </p>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="role-description">Description</Label>
              <Input
                id="role-description"
                placeholder="Optional description"
                value={form.description}
                onChange={(e) => setField("description", e.target.value)}
              />
            </div>

            {saveError && (
              <p className="text-sm text-destructive">{saveError}</p>
            )}
          </div>

          <SheetFooter>
            <Button
              onClick={handleSave}
              disabled={saving || !form.name.trim() || !form.short_name.trim()}
              className="w-full"
            >
              {saving && <Spinner />}
              {saving ? "Saving…" : editingRole ? "Save changes" : "Create role"}
            </Button>
            <SheetClose asChild>
              <Button variant="outline" className="w-full" disabled={saving}>
                Cancel
              </Button>
            </SheetClose>
          </SheetFooter>
        </SheetContent>
      </Sheet>

      <DeleteDialog
        open={!!deletingRole}
        onOpenChange={(open) => { if (!open) setDeletingRole(null) }}
        title="Delete role?"
        description={deletingRole && (
          <><strong>{deletingRole.name}</strong> will be deleted. This will fail if any users are still assigned to this role.</>
        )}
        onConfirm={() => deleteRole(deletingRole!.id)}
        successMessage="Role deleted"
      />
    </>
  )
}
