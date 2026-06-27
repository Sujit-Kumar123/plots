"use client"

import * as React from "react"
import {
  Command,
  LayoutDashboard,
  BarChart2,
  Users,
  FolderOpen,
  FileText,
  Settings2,
  LifeBuoy,
  Send,
  Frame,
  PieChart,
  Map,
  BotMessageSquare,
  PenLine,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import { ThemeToggle } from "@/components/theme-toggle"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      title: "Analytics",
      url: "/dashboard/analytics",
      icon: BarChart2,
    },
    {
      title: "AI Chat",
      url: "/dashboard/chat",
      icon: BotMessageSquare,
    },
    {
      title: "Plot Sheets",
      url: "/dashboard/sheets",
      icon: PenLine,
    },
    {
      title: "Users",
      url: "/dashboard/users",
      icon: Users,
      items: [
        { title: "All Users",    url: "/dashboard/users" },
        { title: "Roles",        url: "/dashboard/users/roles" },
        { title: "Permissions",  url: "/dashboard/users/permissions" },
      ],
    },
    {
      title: "Projects",
      url: "/dashboard/projects",
      icon: FolderOpen,
      items: [
        { title: "All Projects", url: "/dashboard/projects" },
        { title: "Active", url: "/dashboard/projects/active" },
      ],
    },
    {
      title: "Reports",
      url: "/dashboard/reports",
      icon: FileText,
    },
    {
      title: "Settings",
      url: "/dashboard/settings",
      icon: Settings2,
      items: [
        { title: "General", url: "/dashboard/settings" },
        { title: "Team", url: "/dashboard/settings/team" },
        { title: "Billing", url: "/dashboard/settings/billing" },
      ],
    },
  ],
  navSecondary: [
    {
      title: "Support",
      url: "#",
      icon: LifeBuoy,
    },
    {
      title: "Feedback",
      url: "#",
      icon: Send,
    },
  ],
  projects: [
    {
      name: "Design Engineering",
      url: "#",
      icon: Frame,
    },
    {
      name: "Sales & Marketing",
      url: "#",
      icon: PieChart,
    },
    {
      name: "Travel",
      url: "#",
      icon: Map,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/dashboard">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Command className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">Acme Inc</span>
                  <span className="truncate text-xs">Enterprise</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <ThemeToggle />
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  )
}
