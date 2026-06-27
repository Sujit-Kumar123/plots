"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BarChart2,
  Users,
  FolderOpen,
  FileText,
  Settings,
  HelpCircle,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Analytics", href: "/dashboard/analytics", icon: BarChart2 },
  { label: "Users", href: "/dashboard/users", icon: Users },
  { label: "Projects", href: "/dashboard/projects", icon: FolderOpen },
  { label: "Reports", href: "/dashboard/reports", icon: FileText },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-60 flex-col border-r bg-sidebar">
      {/* Brand */}
      <div className="flex h-16 shrink-0 items-center border-b px-6">
        <span className="text-lg font-semibold tracking-tight">MyApp</span>
      </div>

      {/* Main nav */}
      <nav className="flex flex-1 flex-col gap-1 p-3">
        {navItems.map(({ label, href, icon: Icon }) => (
          <Button
            key={href}
            variant={pathname === href ? "secondary" : "ghost"}
            className={cn(
              "w-full justify-start gap-3",
              pathname === href && "font-medium"
            )}
            asChild
          >
            <Link href={href}>
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          </Button>
        ))}
      </nav>

      {/* Bottom section */}
      <div className="shrink-0 border-t p-3 space-y-1">
        <Button variant="ghost" className="w-full justify-start gap-3">
          <HelpCircle className="h-4 w-4 shrink-0" />
          Help
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-destructive hover:text-destructive hover:bg-destructive/10"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          Logout
        </Button>
      </div>
    </aside>
  );
}
