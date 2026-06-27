import { Suspense } from "react"
import Link from "next/link"
import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { fetchSheets } from "@/lib/services/server/sheets"
import { SheetsGrid, SheetsGridSkeleton } from "./_components/sheets-grid"

export const metadata = { title: "Plot Sheets" }

interface Props {
  searchParams: Promise<{ page?: string; page_size?: string; search?: string }>
}

async function SheetsList({ page, page_size, search }: { page: number; page_size: number; search: string }) {
  const data = await fetchSheets({ page, page_size, search: search || undefined })
  return <SheetsGrid data={data} search={search} />
}

export default async function SheetsPage({ searchParams }: Props) {
  const params = await searchParams
  const page      = Math.max(1, Number(params.page      ?? 1))
  const page_size = Math.max(1, Number(params.page_size ?? 12))
  const search    = params.search ?? ""

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Plot Sheets</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Your saved 3D construction drawings.
          </p>
        </div>
        <Button asChild>
          <Link href="/plot">
            <Plus className="size-4" />
            New Sheet
          </Link>
        </Button>
      </div>

      {/* <Separator /> */}

      <Card>
        <CardContent className="pt-6">
          <Suspense key={`${page}-${page_size}-${search}`} fallback={<SheetsGridSkeleton pageSize={page_size} />}>
            <SheetsList page={page} page_size={page_size} search={search} />
          </Suspense>
        </CardContent>
      </Card>
    </div>
  )
}
