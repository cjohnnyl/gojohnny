import { NextRequest, NextResponse } from "next/server";

const PROTECTED_ROUTES = ["/chat", "/plano", "/onboarding"];
const PUBLIC_ROUTES = ["/login"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  const isPublic = PUBLIC_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  // Cookie setado no login via JS e removido no logout.
  // O middleware não tem acesso ao localStorage (roda no Edge Runtime),
  // por isso usamos um cookie leve como sinal de sessão ativa.
  const hasSession = request.cookies.has("has_session");

  // Rota protegida sem sessão → redireciona para login
  if (isProtected && !hasSession) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Raiz → redireciona para login (a página / já faz isso via JS, mas o
  // middleware garante o comportamento mesmo antes da hidratação)
  if (pathname === "/") {
    if (hasSession) {
      return NextResponse.redirect(new URL("/chat", request.url));
    }
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Login com sessão ativa → redireciona para chat
  if (isPublic && hasSession) {
    return NextResponse.redirect(new URL("/chat", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Aplica o middleware em todas as rotas exceto:
     * - _next/static (arquivos estáticos)
     * - _next/image (otimização de imagens)
     * - favicon.ico, ícones e imagens públicas
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
