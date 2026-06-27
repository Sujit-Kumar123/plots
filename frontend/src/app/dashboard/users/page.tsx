import { UserPlus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { UsersTable } from "./_components/users-table"
import { fetchUsers } from "@/lib/services/server/admin-users"
import { fetchRoles } from "@/lib/services/server/roles"

interface Props {
  searchParams: Promise<{ page?: string; page_size?: string }>
}

export default async function UsersPage({ searchParams }: Props) {
  const { page: pageParam, page_size: pageSizeParam } = await searchParams
  const page     = Math.max(1, Number(pageParam     ?? 1))
  const pageSize = Math.max(1, Number(pageSizeParam ?? 10))

  const [data, roles] = await Promise.all([
    fetchUsers({ page, page_size: pageSize }),
    fetchRoles(),
  ])

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Users</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage your team members and their roles.
          </p>
        </div>
        <Button>
          <UserPlus />
          Invite User
        </Button>
      </div>

      <UsersTable
        initialUsers={data.items}
        page={page}
        pageSize={pageSize}
        total={data.total}
        totalPages={data.total_pages}
        roles={roles}
      />
    </div>
  )
}
