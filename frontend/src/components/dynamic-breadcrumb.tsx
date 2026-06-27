"use client"

import { usePathname } from "next/navigation"
import Link from "next/link"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

const LABELS: Record<string, string> = {
  dashboard:  "Dashboard",
  analytics:  "Analytics",
  users:      "Users",
  roles:      "Roles",
  projects:   "Projects",
  active:     "Active",
  reports:    "Reports",
  settings:   "Settings",
  team:       "Team",
  billing:    "Billing",
}

function toLabel(segment: string) {
  return LABELS[segment] ?? segment.charAt(0).toUpperCase() + segment.slice(1)
}

export function DynamicBreadcrumb() {
  const pathname = usePathname()

  // e.g. "/dashboard/users/roles" → ["dashboard", "users", "roles"]
  const segments = pathname.split("/").filter(Boolean)

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {segments.map((segment, index) => {
          const href = "/" + segments.slice(0, index + 1).join("/")
          const isLast = index === segments.length - 1
          const label = toLabel(segment)

          return (
            <span key={href} className="flex items-center gap-1.5">
              {index > 0 && <BreadcrumbSeparator className="hidden md:block" />}
              <BreadcrumbItem className={index < segments.length - 1 ? "hidden md:block" : ""}>
                {isLast ? (
                  <BreadcrumbPage>{label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink asChild>
                    <Link href={href}>{label}</Link>
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </span>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
