import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

function PermissionRowSkeleton() {
  return (
    <div className="flex items-center gap-4 px-6 py-3.5 border-b last:border-b-0">
      <Skeleton className="h-4 w-36 shrink-0" />
      <Skeleton className="h-5 w-28 rounded" />
      <Skeleton className="h-5 w-20 rounded-full" />
      <Skeleton className="h-4 w-64 flex-1" />
      <div className="flex gap-1 ml-auto">
        <Skeleton className="size-7 rounded-md" />
        <Skeleton className="size-7 rounded-md" />
      </div>
    </div>
  )
}

export default function PermissionsLoading() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex flex-col gap-2">
              <Skeleton className="h-5 w-28" />
              <Skeleton className="h-4 w-72" />
            </div>
            <Skeleton className="h-8 w-36 rounded-md" />
          </div>
        </CardHeader>
        <CardContent className="p-0 pb-2">
          {/* Table header */}
          <div className="flex items-center gap-4 px-6 py-3 border-b">
            <Skeleton className="h-3.5 w-12" />
            <Skeleton className="h-3.5 w-10 ml-16" />
            <Skeleton className="h-3.5 w-16 ml-12" />
            <Skeleton className="h-3.5 w-20 ml-10" />
            <Skeleton className="h-3.5 w-14 ml-auto" />
          </div>
          {Array.from({ length: 8 }).map((_, i) => (
            <PermissionRowSkeleton key={i} />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
