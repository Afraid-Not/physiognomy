"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../hooks/useAuth";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { signIn, user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.replace("/");
    }
  }, [user, loading, router]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!email || !password) {
        setError("이메일과 비밀번호를 입력해주세요.");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        await signIn(email, password);
        router.push("/");
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "로그인에 실패했습니다.";
        if (message.includes("Invalid login")) {
          setError("이메일 또는 비밀번호가 올바르지 않습니다.");
        } else {
          setError(message);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [email, password, signIn, router],
  );

  const inputClass =
    "w-full h-12 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:focus:ring-zinc-500 transition-shadow";

  return (
    <div className="flex flex-col items-center justify-center flex-1 p-6">
      <main className="w-full max-w-sm flex flex-col items-center gap-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
            로그인
          </h1>
          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
            점.ZIP 서비스를 이용하려면 로그인해주세요
          </p>
        </div>

        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
          <div>
            <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
              이메일
            </label>
            <input
              type="email"
              placeholder="email@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputClass}
              autoComplete="email"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
              비밀번호
            </label>
            <input
              type="password"
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputClass}
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-12 rounded-full bg-zinc-900 text-white font-medium transition-colors hover:bg-zinc-700 disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300 flex items-center justify-center"
          >
            {isLoading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          계정이 없으신가요?{" "}
          <button
            onClick={() => router.push("/signup")}
            className="text-zinc-900 dark:text-zinc-100 font-medium hover:underline"
          >
            회원가입
          </button>
        </p>
      </main>
    </div>
  );
};

export default LoginPage;
