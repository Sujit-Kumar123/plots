export interface UserProfile {
  fname: string | null
  lname: string | null
  phone: string | null
  company: string | null
  department: string | null
  designation: string | null
  company_role: string | null
  location: string | null
  photo: string | null
}

export interface Permission {
  id: string
  name: string
  code: string
}

export interface RolePermission {
  permission: Permission
}

export interface Role {
  id: string
  name: string
  short_name: string
  role_permissions: RolePermission[]
}

export interface AuthUser {
  id: string
  email: string
  is_active: boolean
  is_verified: boolean
  last_login: string | null
  auth_source: string
  profile: UserProfile | null
  role: Role | null
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
}

export interface ApiResponse<T = unknown> {
  success: boolean
  data: T | null
  message: string | null
  errors: unknown | null
}
