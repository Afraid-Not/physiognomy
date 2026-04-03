"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../hooks/useAuth";

const SignupPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { signUp, user, loading } = useAuth();
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
      if (password.length < 6) {
        setError("비밀번호는 6자 이상이어야 합니다.");
        return;
      }
      if (password !== confirmPassword) {
        setError("비밀번호가 일치하지 않습니다.");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        await signUp(email, password);
        setSuccess(true);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "회원가입에 실패했습니다.";
        if (message.includes("already registered")) {
          setError("이미 가입된 이메일입니다.");
        } else {
          setError(message);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [email, password, confirmPassword, signUp],
  );

  const inputClass =
    "w-full h-12 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:focus:ring-zinc-500 transition-shadow";

  if (success) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 p-6">
        <main className="w-full max-w-sm flex flex-col items-center gap-6 text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-emerald-600 dark:text-emerald-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            회원가입 완료!
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            이메일 인증 후 로그인해주세요.
            <br />
            인증 메일이 <span className="font-medium">{email}</span>로
            발송되었습니다.
          </p>
          <button
            onClick={() => router.push("/login")}
            className="w-full h-12 rounded-full bg-zinc-900 text-white font-medium transition-colors hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
          >
            로그인하러 가기
          </button>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center flex-1 p-6">
      <main className="w-full max-w-sm flex flex-col items-center gap-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
            회원가입
          </h1>
          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
            계정을 만들어 분석 이력을 저장하세요
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
              비밀번호 (6자 이상)
            </label>
            <input
              type="password"
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputClass}
              autoComplete="new-password"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
              비밀번호 확인
            </label>
            <input
              type="password"
              placeholder="비밀번호 확인"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className={inputClass}
              autoComplete="new-password"
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
            {isLoading ? "가입 중..." : "회원가입"}
          </button>
        </form>

        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          이미 계정이 있으신가요?{" "}
          <button
            onClick={() => router.push("/login")}
            className="text-zinc-900 dark:text-zinc-100 font-medium hover:underline"
          >
            로그인
          </button>
        </p>
      </main>
    </div>
  );
};

export default SignupPage;
