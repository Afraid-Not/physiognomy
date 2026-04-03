"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "../hooks/useAuth";

const NavBar = () => {
  const { user, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push("/login");
  };

  if (!user) return null;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-zinc-950/80 backdrop-blur border-b border-zinc-200 dark:border-zinc-800">
      <div className="max-w-4xl mx-auto px-4 h-12 flex items-center justify-between">
        <button
          onClick={() => router.push("/")}
          className="text-sm font-semibold text-zinc-900 dark:text-zinc-100"
        >
          AI 운세
        </button>
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/mypage")}
            className="text-xs text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
          >
            마이페이지
          </button>
          <button
            onClick={handleSignOut}
            className="text-xs text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
          >
            로그아웃
          </button>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
