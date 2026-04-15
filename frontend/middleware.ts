import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

const PROTECTED_ROUTES = ["/chat", "/plano"];
const PUBLIC_ROUTES = ["/login"];
const AUTH_CALLBACK_ROUTES = ["/auth/callback", "/auth/reset-password"];

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet: { name: string; value: string; options?: object }[]) {
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  const isPublic = PUBLIC_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  const isAuthCallback = AUTH_CALLBACK_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  // Auth callback routes são públicas (sem verificação de sessão)
  if (isAuthCallback) {
    return supabaseResponse;
  }

  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Função auxiliar: cria redirect preservando os cookies do Supabase SSR.
  // Sem isso, a sessão recém-criada pelo signInWithPassword é perdida e o
  // usuário é redirecionado de volta ao login em loop infinito.
  function redirectWithCookies(url: URL): NextResponse {
    const redirectResponse = NextResponse.redirect(url);
    supabaseResponse.cookies.getAll().forEach((cookie) => {
      redirectResponse.cookies.set(cookie.name, cookie.value);
    });
    return redirectResponse;
  }

  // Rota protegida sem usuário → redireciona para login
  if (isProtected && !user) {
    const loginUrl = new URL("/login", request.url);
    return redirectWithCookies(loginUrl);
  }

  // Raiz → redireciona para chat (se autenticado) ou login
  if (pathname === "/") {
    if (user) {
      return redirectWithCookies(new URL("/chat", request.url));
    }
    return redirectWithCookies(new URL("/login", request.url));
  }

  // Login com usuário autenticado → redireciona para chat
  if (isPublic && user) {
    return redirectWithCookies(new URL("/chat", request.url));
  }

  return supabaseResponse;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
