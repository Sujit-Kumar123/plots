"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react"
import { useRouter } from "next/navigation"

import {
  login as authLogin,
  register as authRegister,
  logout as authLogout,
  getMe,
} from "@/lib/services/client/auth"
import type { AuthUser } from "@/lib/types/auth"

interface AuthContextValue {
  user: AuthUser | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (
    email: string,
    password: string,
    fname?: string,
    lname?: string,
  ) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  const refreshUser = useCallback(async () => {
    setUser(await getMe())
  }, [])

  useEffect(() => {
    refreshUser().finally(() => setLoading(false))
  }, [refreshUser])

  const login = async (email: string, password: string) => {
    const { user } = await authLogin(email, password)
    setUser(user)
    router.push("/dashboard")
  }

  const register = async (
    email: string,
    password: string,
    fname?: string,
    lname?: string,
  ) => {
    const { user } = await authRegister(email, password, fname, lname)
    setUser(user)
    router.push("/dashboard")
  }

  const logout = async () => {
    try {
      await authLogout()
    } catch {
      // Proceed with client-side cleanup even if the server call fails
    } finally {
      setUser(null)
      // Full navigation ensures the browser flushes Set-Cookie headers before
      // the next request, so the middleware won't redirect back to /dashboard.
      window.location.replace("/login")
    }
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>")
  return ctx
}
