import { PermissionsManager } from "./_components/permissions-manager"
import { fetchPermissions } from "@/lib/services/server/permissions"

interface Props {
  searchParams: Promise<{ page?: string; page_size?: string }>
}

export default async function PermissionsPage({ searchParams }: Props) {
  const { page: pageParam, page_size: pageSizeParam } = await searchParams
  const page     = Math.max(1, Number(pageParam     ?? 1))
  const pageSize = Math.max(1, Number(pageSizeParam ?? 10))

  const data = await fetchPermissions({ page, page_size: pageSize })

  return (
    <div className="flex flex-col gap-6 p-6">
      {data.fetchError && (
        <p className="text-sm text-destructive">{data.fetchError}</p>
      )}
      <PermissionsManager
        permissions={data.items}
        page={page}
        pageSize={pageSize}
        total={data.total}
        totalPages={data.total_pages}
      />
    </div>
  )
}
