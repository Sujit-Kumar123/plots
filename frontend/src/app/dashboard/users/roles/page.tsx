import { Separator } from "@/components/ui/separator"
import { RolesManager } from "./_components/roles-manager"
import { PermissionMatrix } from "./_components/permission-matrix"
import { fetchRoles } from "@/lib/services/server/roles"
import { fetchPermissions } from "@/lib/services/server/permissions"

export default async function RolesPage() {
  const [roles, permissions] = await Promise.all([fetchRoles(), fetchPermissions()])

  return (
    <div className="flex flex-col gap-6 p-6">
      <RolesManager roles={roles} />

      <Separator />

      <PermissionMatrix roles={roles}  />
    </div>
  )
}
