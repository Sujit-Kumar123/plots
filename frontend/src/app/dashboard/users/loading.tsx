import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

function TableRowSkeleton() {
  return (
    <div className="flex items-center gap-4 px-6 py-3.5 border-b last:border-b-0">
      {/* User cell */}
      <div className="flex items-center gap-3 w-48 shrink-0">
        <Skeleton className="size-8 rounded-full" />
        <Skeleton className="h-4 w-28" />
      </div>
      {/* Email */}
      <Skeleton className="h-4 w-44 flex-1" />
      {/* Role */}
      <Skeleton className="h-5 w-20 rounded-full" />
      {/* Status */}
      <Skeleton className="h-5 w-16 rounded-full ml-4" />
      {/* Joined */}
      <Skeleton className="h-4 w-24 ml-4" />
      {/* Actions */}
      <div className="flex gap-1 ml-auto">
        <Skeleton className="size-7 rounded-md" />
        <Skeleton className="size-7 rounded-md" />
      </div>
    </div>
  )
}

export default function UsersLoading() {
  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-7 w-20" />
          <Skeleton className="h-4 w-56" />
        </div>
        <Skeleton className="h-9 w-28 rounded-md" />
      </div>

      {/* Table card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-4">
            <div className="flex flex-col gap-2">
              <Skeleton className="h-5 w-20" />
              <Skeleton className="h-4 w-16" />
            </div>
            <Skeleton className="h-9 w-64 rounded-md" />
          </div>
        </CardHeader>
        <CardContent className="p-0 pb-2">
          {/* Table header */}
          <div className="flex items-center gap-4 px-6 py-3 border-b">
            <Skeleton className="h-3.5 w-16" />
            <Skeleton className="h-3.5 w-12 ml-[7.5rem]" />
            <Skeleton className="h-3.5 w-10 ml-[8rem]" />
            <Skeleton className="h-3.5 w-12 ml-6" />
            <Skeleton className="h-3.5 w-14 ml-6" />
            <Skeleton className="h-3.5 w-14 ml-auto" />
          </div>
          {/* Table rows */}
          {Array.from({ length: 8 }).map((_, i) => (
            <TableRowSkeleton key={i} />
          ))}
          {/* Pagination */}
          <div className="flex items-center justify-between px-6 py-3">
            <Skeleton className="h-4 w-36" />
            <div className="flex items-center gap-2">
              <Skeleton className="h-8 w-8 rounded-md" />
              <Skeleton className="h-8 w-8 rounded-md" />
              <Skeleton className="h-8 w-8 rounded-md" />
              <Skeleton className="h-8 w-8 rounded-md" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
