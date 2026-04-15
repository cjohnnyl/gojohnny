"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";

type Props = {
  name: string;
  email: string;
};

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export default function UserMenu({ name, email }: Props) {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const supabase = createClient();

  async function handleLogout() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 hover:opacity-80 transition"
        aria-label="Menu do usuário"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-violet-400 flex items-center justify-center text-white text-xs font-bold">
          {getInitials(name || email)}
        </div>
        <span className="text-sm text-zinc-300 hidden sm:block">
          {name || email.split("@")[0]}
        </span>
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 top-10 z-20 bg-zinc-800 border border-zinc-700 rounded-xl p-4 min-w-[200px] shadow-xl">
            <p className="text-white font-medium text-sm truncate">{name}</p>
            <p className="text-zinc-400 text-xs truncate mb-3">{email}</p>
            <button
              onClick={handleLogout}
              className="text-sm text-zinc-300 hover:text-red-400 transition w-full text-left"
            >
              Sair da conta
            </button>
          </div>
        </>
      )}
    </div>
  );
}
