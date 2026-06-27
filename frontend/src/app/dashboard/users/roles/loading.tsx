import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

function RoleCardSkeleton() {
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <Skeleton className="size-9 rounded-lg" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
        <Skeleton className="h-5 w-28 mt-3" />
        <Skeleton className="h-3.5 w-full mt-1" />
        <Skeleton className="h-3.5 w-3/4" />
      </CardHeader>
      <CardContent className="pb-2">
        <Skeleton className="h-3.5 w-32" />
      </CardContent>
      <CardFooter className="mt-auto pt-2 flex gap-1">
        <Skeleton className="h-8 flex-1 rounded-md" />
        <Skeleton className="size-8 rounded-md" />
      </CardFooter>
    </Card>
  )
}

function PermissionMatrixSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <Skeleton className="h-5 w-44" />
        <Skeleton className="h-4 w-72" />
      </div>
      <div className="rounded-lg border overflow-hidden">
        {/* Header row */}
        <div className="flex items-center gap-4 px-4 py-3 bg-muted/40 border-b">
          <Skeleton className="h-4 w-32" />
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-4 w-20 ml-auto first:ml-8" />
          ))}
        </div>
        {/* Permission rows */}
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 px-4 py-3 border-b last:border-b-0">
            <div className="flex flex-col gap-1 w-48 shrink-0">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-3 w-44" />
            </div>
            {Array.from({ length: 3 }).map((_, j) => (
              <Skeleton key={j} className="size-5 rounded ml-auto first:ml-8" />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function RolesLoading() {
  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-7 w-44" />
          <Skeleton className="h-4 w-72" />
        </div>
        <Skeleton className="h-9 w-28 rounded-md" />
      </div>

      {/* Role cards grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <RoleCardSkeleton key={i} />
        ))}
      </div>

      <Separator />

      {/* Permission matrix */}
      <PermissionMatrixSkeleton />
    </div>
  )
}
