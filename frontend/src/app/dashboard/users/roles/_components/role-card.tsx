"use client"

import { Crown, ShieldCheck, ShieldHalf, Pencil, Trash2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { ApiRole } from "../_data"

function getRoleVisuals(shortName: string): {
  icon: React.ElementType
  badge: "default" | "secondary" | "outline"
  color: string
} {
  switch (shortName) {
    case "superadmin": return { icon: Crown,       badge: "default",   color: "text-primary" }
    case "admin":      return { icon: Crown,       badge: "default",   color: "text-primary" }
    case "member":     return { icon: ShieldHalf,  badge: "outline",   color: "text-primary" }
    default:           return { icon: ShieldCheck, badge: "secondary", color: "text-primary" }
  }
}

interface RoleCardProps {
  role: ApiRole
  onEdit?: (role: ApiRole) => void
  onDelete?: (role: ApiRole) => void
}

export function RoleCard({ role, onEdit, onDelete }: RoleCardProps) {
  const { icon: Icon, badge, color } = getRoleVisuals(role.short_name)
  const permCount = role.role_permissions.length

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className={`flex size-9 items-center justify-center rounded-lg bg-primary/10 ${color}`}>
            <Icon className="size-5" />
          </div>
          <Badge variant={badge}>{role.name}</Badge>
        </div>
        <CardTitle className="text-base mt-3">{role.name}</CardTitle>
        <CardDescription className="text-xs leading-relaxed">
          {role.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="pb-2">
        <p className="text-xs text-muted-foreground">
          <span className="font-semibold text-foreground">{permCount}</span>{" "}
          permission{permCount !== 1 ? "s" : ""} assigned
        </p>
      </CardContent>

      <CardFooter className="mt-auto pt-2 flex gap-1">
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={() => onEdit?.(role)}
        >
          <Pencil />
          Edit
        </Button>
        <Button
          variant="destructive"
          size="icon-sm"
          aria-label="Delete role"
          disabled={role.short_name === "superadmin"}
          onClick={() => onDelete?.(role)}
        >
          <Trash2 />
        </Button>
      </CardFooter>
    </Card>
  )
}
