import { TrendingUp, TrendingDown, Users, MousePointerClick, Clock, BarChart2 } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"

const STATS = [
  { label: "Total Sessions",        value: "48,295", change: "+12.5%", up: true,  icon: BarChart2        },
  { label: "Unique Visitors",       value: "21,430", change: "+8.1%",  up: true,  icon: Users            },
  { label: "Avg. Session Duration", value: "3m 42s", change: "-0.4%",  up: false, icon: Clock            },
  { label: "Click-through Rate",    value: "5.27%",  change: "+1.2%",  up: true,  icon: MousePointerClick },
]

export default function AnalyticsPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold">Analytics</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Track visitor trends across desktop and mobile.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {STATS.map(({ label, value, change, up, icon: Icon }) => (
          <Card key={label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <p className="text-sm font-medium text-muted-foreground">{label}</p>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{value}</p>
              <p className={`text-xs mt-1 flex items-center gap-1 ${up ? "text-emerald-600 dark:text-emerald-400" : "text-destructive"}`}>
                {up ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
                {change} from last period
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Interactive area chart */}
      <ChartAreaInteractive />
    </div>
  )
}
