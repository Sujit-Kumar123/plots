"use client"

import * as React from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  SheetClose,
} from "@/components/ui/sheet"
import { createPermission, updatePermission, fetchMissingPermissionCodes } from "@/lib/services/server/permissions"
import type { ApiPermission } from "@/lib/types/roles"

const EMPTY_FORM = { name: "", code: "", description: "" }

function codeToName(code: string): string {
  if (code === "*:*") return "Superadmin (All)"
  const [resource, action] = code.split(":")
  if (!resource || !action) return code
  return `${action.charAt(0).toUpperCase()}${action.slice(1)} ${resource.charAt(0).toUpperCase()}${resource.slice(1)}`
}

interface PermissionSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  editingPerm: ApiPermission | null
}

export function PermissionSheet({ open, onOpenChange, editingPerm }: PermissionSheetProps) {
  const [form, setForm] = React.useState(EMPTY_FORM)
  const [saving, setSaving] = React.useState(false)
  const [saveError, setSaveError] = React.useState<string | null>(null)
  const [missingCodes, setMissingCodes] = React.useState<string[]>([])

  React.useEffect(() => {
    if (open) {
      setForm(
        editingPerm
          ? { name: editingPerm.name, code: editingPerm.code, description: editingPerm.description ?? "" }
          : EMPTY_FORM,
      )
      setSaveError(null)
      if (!editingPerm) {
        fetchMissingPermissionCodes().then(setMissingCodes)
      } else {
        setMissingCodes([])
      }
    }
  }, [open, editingPerm])

  function setField(key: keyof typeof EMPTY_FORM, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  function applySuggestion(code: string) {
    setForm((prev) => ({
      ...prev,
      code,
      name: prev.name.trim() ? prev.name : codeToName(code),
    }))
  }

  async function handleSave() {
    setSaving(true)
    setSaveError(null)

    const result = editingPerm
      ? await updatePermission(editingPerm.id, {
          name: form.name,
          code: form.code,
          description: form.description || undefined,
        })
      : await createPermission({
          name: form.name,
          code: form.code,
          description: form.description || undefined,
        })

    setSaving(false)

    if (result.error) {
      setSaveError(result.error)
      toast.error(result.error)
      return
    }

    onOpenChange(false)
    toast.success(editingPerm ? "Permission updated" : "Permission created")
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right">
        <SheetHeader>
          <SheetTitle>{editingPerm ? "Edit Permission" : "Create Permission"}</SheetTitle>
          <SheetDescription>
            {editingPerm
              ? `Update details for "${editingPerm.name}".`
              : "Add a new permission to the system."}
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-col gap-5 px-4 py-2">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="perm-name">Name</Label>
            <Input
              id="perm-name"
              placeholder="e.g. Read Users"
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
              disabled={saving}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="perm-code">Code</Label>
            <Input
              id="perm-code"
              placeholder="e.g. users:read"
              value={form.code}
              onChange={(e) => setField("code", e.target.value)}
              disabled={saving}
              className="font-mono"
            />
            <p className="text-xs text-muted-foreground">
              Format: <code className="font-mono">resource:action</code> — e.g.{" "}
              <code className="font-mono">users:read</code>,{" "}
              <code className="font-mono">roles:write</code>
            </p>
            {missingCodes.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {missingCodes.map((code) => (
                  <Badge
                    key={code}
                    variant="outline"
                    className="cursor-pointer font-mono text-xs hover:bg-muted transition-colors"
                    onClick={() => applySuggestion(code)}
                  >
                    {code}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="perm-description">Description</Label>
            <Input
              id="perm-description"
              placeholder="Optional description"
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
              disabled={saving}
            />
          </div>

          {saveError && (
            <p className="text-sm text-destructive">{saveError}</p>
          )}
        </div>

        <SheetFooter>
          <Button
            onClick={handleSave}
            disabled={saving || !form.name.trim() || !form.code.trim()}
            className="w-full"
          >
            {saving && <Spinner />}
            {saving ? "Saving…" : editingPerm ? "Save changes" : "Create permission"}
          </Button>
          <SheetClose asChild>
            <Button variant="outline" className="w-full" disabled={saving}>
              Cancel
            </Button>
          </SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
