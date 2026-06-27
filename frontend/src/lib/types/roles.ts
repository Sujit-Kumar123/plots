export interface ApiPermission {
  id: string
  name: string
  code: string
  description: string
  created_at: string
}

export interface PaginatedPermissions {
  items: ApiPermission[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ListPermissionsParams {
  page?: number
  page_size?: number
}

export interface ApiRolePermission {
  id: string
  permission: ApiPermission
}

export interface ApiRole {
  id: string
  name: string
  short_name: string
  description: string
  created_at: string
  role_permissions: ApiRolePermission[]
}
