import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Users, BarChart2, FolderOpen, FileText } from "lucide-react";

const stats = [
  { title: "Total Users", value: "1,234", icon: Users, change: "+12% from last month" },
  { title: "Revenue", value: "$45,678", icon: BarChart2, change: "+8.2% from last month" },
  { title: "Active Projects", value: "23", icon: FolderOpen, change: "+3 from last month" },
  { title: "Reports", value: "89", icon: FileText, change: "+5 from last month" },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Welcome back! Here&apos;s an overview of your workspace.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map(({ title, value, icon: Icon, change }) => (
          <Card key={title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {title}
              </CardTitle>
              <div className="flex items-center justify-center rounded-md bg-primary/10 p-1.5">
                <Icon className="h-4 w-4 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{value}</p>
              <p className="text-xs text-primary/70 mt-1">{change}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
