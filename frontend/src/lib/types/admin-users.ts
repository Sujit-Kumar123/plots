export interface AdminUser {
  id: string
  email: string
  is_active: boolean
  is_verified: boolean
  last_login: string | null
  created_at: string
  updated_at: string
  role: {
    id: string
    name: string
    short_name: string
    description: string
  }
  profile: {
    id: string
    fname: string
    lname: string
    phone: string | null
    company: string | null
    department: string | null
    designation: string | null
    photo: string | null
  } | null
}

export interface PaginatedUsers {
  items: AdminUser[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ListUsersParams {
  page?: number
  page_size?: number
  role?: string
  is_active?: boolean
}
