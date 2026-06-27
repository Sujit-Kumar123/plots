import { NextRequest, NextResponse } from "next/server"

const PROTECTED = "/dashboard"
const AUTH_PAGES = ["/login", "/signup", "/forgot-password", "/reset-password"]

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get("access_token")?.value

  // Unauthenticated user trying to reach a protected page
  if (pathname.startsWith(PROTECTED) && !token) {
    const url = request.nextUrl.clone()
    url.pathname = "/login"
    url.searchParams.set("next", pathname)
    return NextResponse.redirect(url)
  }

  // Authenticated user trying to reach an auth page
  if (AUTH_PAGES.some((p) => pathname === p) && token) {
    const url = request.nextUrl.clone()
    url.pathname = "/dashboard"
    url.searchParams.delete("next")
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/login",
    "/signup",
    "/forgot-password",
    "/reset-password",
  ],
}
