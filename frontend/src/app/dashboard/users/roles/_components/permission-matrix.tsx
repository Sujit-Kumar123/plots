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
import type { ApiRole } from "../_data"

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

function PermCell({ allowed }: { allowed: boolean }) {
  return (
    <TableCell className="text-center">
      {allowed ? (
        <span className="inline-flex items-center justify-center size-5 rounded-full bg-primary/15">
          <Check className="size-3 text-primary" />
        </span>
      ) : (
        <span className="inline-flex items-center justify-center size-5 rounded-full bg-muted">
          <Minus className="size-3 text-muted-foreground" />
        </span>
      )}
    </TableCell>
  )
}

interface PermissionMatrixProps {
  roles: ApiRole[]
}

export function PermissionMatrix({ roles }: PermissionMatrixProps) {
  // Collect all unique permissions across all roles
  const permMap = new Map<string, { name: string; code: string }>()
  for (const role of roles) {
    for (const rp of role.role_permissions) {
      const { id, name, code } = rp.permission
      if (!permMap.has(id)) permMap.set(id, { name, code })
    }
  }
  const allPerms = Array.from(permMap.entries()).map(([id, p]) => ({ id, ...p }))

  // Group by category derived from permission code prefix
  const categories = Array.from(new Set(allPerms.map((p) => getCategory(p.code))))

  // Build a lookup: permissionId → Set of role ids that have it
  const roleHasPerm = new Map<string, Set<string>>()
  for (const role of roles) {
    for (const rp of role.role_permissions) {
      const set = roleHasPerm.get(rp.permission.id) ?? new Set()
      set.add(role.id)
      roleHasPerm.set(rp.permission.id, set)
    }
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-base font-semibold">Permission Matrix</h2>
        <p className="text-muted-foreground text-sm mt-0.5">
          Overview of what each role is allowed to do.
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="pl-6 w-[220px]">Permission</TableHead>
                {roles.map((role) => {
                  const Icon = getRoleIcon(role.short_name)
                  return (
                    <TableHead key={role.id} className="text-center w-[110px]">
                      <div className="flex flex-col items-center gap-1">
                        <Icon className="size-4 text-primary" />
                        <span>{role.name}</span>
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
                  {allPerms
                    .filter((p) => getCategory(p.code) === category)
                    .map((perm) => (
                      <TableRow key={perm.id}>
                        <TableCell className="pl-6 font-medium text-sm">
                          {perm.name}
                        </TableCell>
                        {roles.map((role) => (
                          <PermCell
                            key={role.id}
                            allowed={roleHasPerm.get(perm.id)?.has(role.id) ?? false}
                          />
                        ))}
                      </TableRow>
                    ))}
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
