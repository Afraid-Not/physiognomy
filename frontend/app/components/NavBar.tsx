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

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-zinc-900/80 backdrop-blur border-b border-zinc-200 dark:border-zinc-800 rounded-t-2xl">
      <div className="px-4 h-12 flex items-center justify-between">
        <button
          onClick={() => router.push("/")}
          className="text-sm font-semibold text-zinc-900 dark:text-zinc-100"
        >
          점zip
        </button>
        {user && (
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
        )}
      </div>
    </nav>
  );
};

export default NavBar;
