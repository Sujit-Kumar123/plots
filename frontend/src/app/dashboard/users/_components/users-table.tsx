"use client"

import * as React from "react"
import { usePathname, useSearchParams, useRouter } from "next/navigation"
import { DataTablePagination } from "@/components/ui/data-table-pagination"
import { Search, Pencil, Trash2 } from "lucide-react"
import { toast } from "sonner"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { DeleteDialog } from "@/components/ui/delete-dialog"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  SheetClose,
} from "@/components/ui/sheet"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { AdminUser } from "@/lib/types/admin-users"
import type { ApiRole } from "@/lib/types/roles"
import { updateUser, deleteUser } from "@/lib/services/server/admin-users"

function roleBadgeVariant(roleName: string): "default" | "secondary" | "outline" {
  const lower = roleName.toLowerCase()
  if (lower === "admin" || lower === "super admin") return "default"
  if (lower === "member") return "secondary"
  return "outline"
}

function getInitials(fname: string, lname: string) {
  return `${fname[0] ?? ""}${lname[0] ?? ""}`.toUpperCase()
}

function getFullName(profile: AdminUser["profile"]): string {
  if (!profile) return "—"
  return `${profile.fname} ${profile.lname}`.trim()
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

interface UsersTableProps {
  initialUsers: AdminUser[]
  roles: ApiRole[]
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export function UsersTable({ initialUsers, roles, page, pageSize, total, totalPages }: UsersTableProps) {
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

  const [editingUser, setEditingUser] = React.useState<AdminUser | null>(null)
  const [editRoleId, setEditRoleId] = React.useState("")
  const [editIsActive, setEditIsActive] = React.useState("true")
  const [saving, setSaving] = React.useState(false)
  const [saveError, setSaveError] = React.useState<string | null>(null)

  const [deletingUser, setDeletingUser] = React.useState<AdminUser | null>(null)

  function openEdit(user: AdminUser) {
    setEditingUser(user)
    setEditRoleId(user.role.id)
    setEditIsActive(String(user.is_active))
    setSaveError(null)
  }

  async function handleSave() {
    if (!editingUser) return
    setSaving(true)
    setSaveError(null)

    const result = await updateUser(editingUser.id, {
      role_id: editRoleId,
      is_active: editIsActive === "true",
    })

    setSaving(false)

    if (result.error) {
      setSaveError(result.error)
      toast.error(result.error)
      return
    }

    setEditingUser(null)
    toast.success("User updated successfully")
  }

  const filtered = initialUsers.filter((u) => {
    const name = getFullName(u.profile).toLowerCase()
    const q = search.toLowerCase()
    return (
      name.includes(q) ||
      u.email.toLowerCase().includes(q) ||
      u.role.name.toLowerCase().includes(q)
    )
  })

  return (
    <>
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-4">
            <div>
              <CardTitle className="text-base">All Users</CardTitle>
              <CardDescription>
                {`${filtered.length} user${filtered.length !== 1 ? "s" : ""}`}
              </CardDescription>
            </div>
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
              <Input
                placeholder="Search users..."
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
                <TableHead className="pl-6">User</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead className="pr-6 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="py-10 text-center text-muted-foreground">
                    No users found.
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((user) => {
                  const name = getFullName(user.profile)
                  const fname = user.profile?.fname ?? ""
                  const lname = user.profile?.lname ?? ""
                  const isActive = user.is_active
                  return (
                    <TableRow key={user.id}>
                      <TableCell className="pl-6">
                        <div className="flex items-center gap-3">
                          <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold">
                            {getInitials(fname, lname)}
                          </div>
                          <span className="font-medium">{name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{user.email}</TableCell>
                      <TableCell>
                        <Badge variant={roleBadgeVariant(user.role.name)}>{user.role.name}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={isActive ? "default" : "outline"}
                          className={
                            isActive
                              ? "bg-emerald-500/15 text-emerald-600 border-emerald-500/20 dark:text-emerald-400"
                              : "text-muted-foreground"
                          }
                        >
                          <span
                            className={`mr-1 size-1.5 rounded-full inline-block ${
                              isActive ? "bg-emerald-500" : "bg-muted-foreground"
                            }`}
                          />
                          {isActive ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatDate(user.created_at)}
                      </TableCell>
                      <TableCell className="pr-6 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            aria-label="Edit user"
                            onClick={() => openEdit(user)}
                          >
                            <Pencil />
                          </Button>
                          <Button
                            variant="destructive"
                            size="icon-sm"
                            aria-label="Delete user"
                            onClick={() => setDeletingUser(user)}
                          >
                            <Trash2 />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })
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

      {/* Edit Sheet */}
      <Sheet open={!!editingUser} onOpenChange={(open) => { if (!open) setEditingUser(null) }}>
        <SheetContent side="right">
          <SheetHeader>
            <SheetTitle>Edit User</SheetTitle>
            <SheetDescription>
              {editingUser ? getFullName(editingUser.profile) : ""}
              {editingUser && (
                <span className="block text-xs mt-0.5">{editingUser.email}</span>
              )}
            </SheetDescription>
          </SheetHeader>

          <div className="flex flex-col gap-5 px-4 py-2">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="edit-role">Role</Label>
              <Select value={editRoleId} onValueChange={setEditRoleId}>
                <SelectTrigger id="edit-role" className="w-full">
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((r) => (
                    <SelectItem key={r.id} value={r.id}>
                      {r.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="edit-status">Status</Label>
              <Select value={editIsActive} onValueChange={setEditIsActive}>
                <SelectTrigger id="edit-status" className="w-full">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Active</SelectItem>
                  <SelectItem value="false">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {saveError && (
              <p className="text-sm text-destructive">{saveError}</p>
            )}
          </div>

          <SheetFooter>
            <Button onClick={handleSave} disabled={saving} className="w-full">
              {saving && <Spinner />}
              {saving ? "Saving…" : "Save changes"}
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
        open={!!deletingUser}
        onOpenChange={(open) => { if (!open) setDeletingUser(null) }}
        title="Delete user?"
        description={deletingUser && (
          <><strong>{getFullName(deletingUser.profile)}</strong> ({deletingUser.email}) will be soft-deleted and can no longer log in. This action cannot be undone from the UI.</>
        )}
        onConfirm={() => deleteUser(deletingUser!.id)}
        successMessage="User deleted"
      />
    </>
  )
}
