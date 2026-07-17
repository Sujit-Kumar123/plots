"use client"

import * as React from "react"
import { Check, Minus } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Crown, ShieldCheck, ShieldHalf } from "lucide-react"
import { toast } from "sonner"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import {
  assignPermissionToRole,
  unassignPermissionFromRole,
} from "@/lib/services/server/permissions"
import type { ApiPermission, ApiRole } from "../_data"

function getRoleIcon(shortName: string): React.ElementType {
  switch (shortName) {
    case "superadmin":
    case "admin":  return Crown
    case "member": return ShieldHalf
    default:       return ShieldCheck
  }
}

function getCategory(code: string): string {
  if (code === "*:*") return "System"
  const prefix = code.split(":")[0]
  return prefix.charAt(0).toUpperCase() + prefix.slice(1)
}

function buildAssignedMap(roles: ApiRole[]): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>()
  for (const role of roles) {
    map.set(role.id, new Set(role.role_permissions.map((rp) => rp.permission.id)))
  }
  return map
}

interface PermCellProps {
  allowed: boolean
  pending: boolean
  disabled: boolean
  permName: string
  roleName: string
  onClick: () => void
}

function PermCell({ allowed, pending, disabled, permName, roleName, onClick }: PermCellProps) {
  const tooltip = disabled
    ? `${roleName} has wildcard (*:*) — all permissions granted`
    : pending
      ? "Saving…"
      : allowed
        ? `Remove "${permName}" from ${roleName}`
        : `Assign "${permName}" to ${roleName}`

  return (
    <TableCell className="text-center">
      <TooltipProvider delayDuration={200}>
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              onClick={onClick}
              disabled={disabled || pending}
              className="group relative inline-flex items-center justify-center size-7 rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed cursor-pointer"
              aria-label={tooltip}
            >
              {pending && (
                <span className="absolute inset-0 rounded-full border-2 border-muted border-t-primary animate-spin" />
              )}

              {allowed ? (
                <span className={`inline-flex items-center justify-center size-5 rounded-full transition-colors ${
                  pending ? "bg-primary/10" : "bg-primary/15 group-hover:bg-destructive/15"
                }`}>
                  <Check className={`size-3 transition-colors ${
                    pending ? "text-primary/40" : "text-primary group-hover:text-destructive"
                  }`} />
                </span>
              ) : (
                <span className={`inline-flex items-center justify-center size-5 rounded-full transition-colors ${
                  pending ? "bg-muted/40" : "bg-muted group-hover:bg-primary/15"
                }`}>
                  <Minus className={`size-3 transition-colors ${
                    pending ? "text-muted-foreground/40" : "text-muted-foreground group-hover:text-primary"
                  }`} />
                </span>
              )}
            </button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>{tooltip}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </TableCell>
  )
}

interface PermissionMatrixProps {
  roles: ApiRole[]
  allPermissions: ApiPermission[]
}

export function PermissionMatrix({ roles, allPermissions }: PermissionMatrixProps) {
  const [assigned, setAssigned] = React.useState(() => buildAssignedMap(roles))
  const [pending, setPending] = React.useState<Set<string>>(new Set())

  // Roles with *:* wildcard get all cells shown as checked and non-editable
  const wildcardRoleIds = React.useMemo(
    () =>
      new Set(
        roles
          .filter((r) => r.role_permissions.some((rp) => rp.permission.code === "*:*"))
          .map((r) => r.id),
      ),
    [roles],
  )

  // Show all permissions except the wildcard *:* entry itself
  const perms = allPermissions.filter((p) => p.code !== "*:*")
  const categories = Array.from(new Set(perms.map((p) => getCategory(p.code))))

  async function togglePermission(permId: string, roleId: string) {
    const key = `${permId}_${roleId}`
    const isAssigned = assigned.get(roleId)?.has(permId) ?? false

    // Optimistic update
    setPending((prev) => new Set(prev).add(key))
    setAssigned((prev) => {
      const next = new Map(prev)
      const set = new Set(next.get(roleId) ?? [])
      isAssigned ? set.delete(permId) : set.add(permId)
      next.set(roleId, set)
      return next
    })

    const result = isAssigned
      ? await unassignPermissionFromRole(permId, roleId)
      : await assignPermissionToRole(permId, roleId)

    setPending((prev) => {
      const next = new Set(prev)
      next.delete(key)
      return next
    })

    if (result.error) {
      // Revert on failure
      setAssigned((prev) => {
        const next = new Map(prev)
        const set = new Set(next.get(roleId) ?? [])
        isAssigned ? set.add(permId) : set.delete(permId)
        next.set(roleId, set)
        return next
      })
      toast.error(result.error)
    } else {
      toast.success(isAssigned ? "Permission removed" : "Permission assigned")
    }
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-base font-semibold">Permission Matrix</h2>
        <p className="text-muted-foreground text-sm mt-0.5">
          Click a cell to assign or remove a permission for a role.
          Roles with <code className="text-xs font-mono">*:*</code> wildcard access cannot be individually edited.
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="pl-6 w-[220px]">Permission</TableHead>
                  {roles.map((role) => {
                    const Icon = getRoleIcon(role.short_name)
                    const isWildcard = wildcardRoleIds.has(role.id)
                    return (
                      <TableHead key={role.id} className="text-center w-[120px]">
                        <div className="flex flex-col items-center gap-1">
                          <Icon className="size-4 text-primary" />
                          <span>{role.name}</span>
                          {isWildcard && (
                            <span className="text-[10px] text-muted-foreground font-mono">*:*</span>
                          )}
                        </div>
                      </TableHead>
                    )
                  })}
                </TableRow>
              </TableHeader>
              <TableBody>
                {categories.map((category) => (
                  <React.Fragment key={category}>
                    <TableRow className="bg-muted/40 hover:bg-muted/40">
                      <TableCell
                        colSpan={roles.length + 1}
                        className="pl-6 py-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                      >
                        {category}
                      </TableCell>
                    </TableRow>
                    {perms
                      .filter((p) => getCategory(p.code) === category)
                      .map((perm) => (
                        <TableRow key={perm.id}>
                          <TableCell className="pl-6">
                            <div className="text-sm font-medium">{perm.name}</div>
                            <div className="text-xs text-muted-foreground font-mono">{perm.code}</div>
                          </TableCell>
                          {roles.map((role) => {
                            const isWildcard = wildcardRoleIds.has(role.id)
                            const isAllowed = isWildcard || (assigned.get(role.id)?.has(perm.id) ?? false)
                            const isPending = pending.has(`${perm.id}_${role.id}`)
                            return (
                              <PermCell
                                key={role.id}
                                allowed={isAllowed}
                                pending={isPending}
                                disabled={isWildcard}
                                permName={perm.name}
                                roleName={role.name}
                                onClick={() => togglePermission(perm.id, role.id)}
                              />
                            )
                          })}
                        </TableRow>
                      ))}
                  </React.Fragment>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
