"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import AuthGuard from "../components/AuthGuard";
import NavBar from "../components/NavBar";
import { useAuth } from "../hooks/useAuth";
import { supabase } from "../lib/supabase";

const HOURS = Array.from({ length: 24 }, (_, i) => i);

const SajuPage = () => {
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [hour, setHour] = useState("");
  const [gender, setGender] = useState<"male" | "female" | "">("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { getAccessToken } = useAuth();

  // 프로필에서 생년월일 자동 입력
  useEffect(() => {
    supabase
      .from("profiles")
      .select("birth_year, birth_month, birth_day, birth_hour, gender")
      .single()
      .then(({ data }) => {
        if (!data) return;
        if (data.birth_year) setYear(String(data.birth_year));
        if (data.birth_month) setMonth(String(data.birth_month));
        if (data.birth_day) setDay(String(data.birth_day));
        if (data.birth_hour !== null) setHour(String(data.birth_hour));
        if (data.gender) setGender(data.gender);
      });
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!year || !month || !day || hour === "" || !gender) {
      setError("모든 항목을 입력해주세요.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setLoadingStep("사주를 계산하고 있어요...");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const token = await getAccessToken();
      const res = await fetch(`${apiUrl}/api/saju`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          birth_year: parseInt(year),
          birth_month: parseInt(month),
          birth_day: parseInt(day),
          birth_hour: parseInt(hour),
          gender,
          stream: true,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail ?? `분석 실패 (${res.status})`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("스트리밍을 시작할 수 없습니다.");

      const decoder = new TextDecoder();
      let buffer = "";
      let sajuData: Record<string, unknown> | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const json_str = line.slice(6);
          try {
            const msg = JSON.parse(json_str);

            if (msg.type === "classified") {
              sajuData = msg.data;
              if (msg.hero)
                sessionStorage.setItem("heroMatch", JSON.stringify(msg.hero));
              setLoadingStep("사주 지식을 찾고 있어요...");
            } else if (msg.type === "chunk") {
              setLoadingStep("사주 분석을 작성하고 있어요...");
            } else if (msg.type === "done") {
              sessionStorage.setItem(
                "sajuResult",
                JSON.stringify({
                  saju: sajuData,
                  analysis: msg.data,
                }),
              );
              router.push("/saju/result");
              return;
            } else if (msg.type === "error") {
              throw new Error(msg.data);
            }
          } catch {
            // JSON parse error for incomplete chunks
          }
        }
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.",
      );
    } finally {
      setIsLoading(false);
      setLoadingStep("");
    }
  }, [year, month, day, hour, gender, router]);

  const inputClass =
    "w-full h-12 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:focus:ring-zinc-500 transition-shadow";

  return (
    <AuthGuard>
      <NavBar />
      <div className="flex flex-col items-center justify-center min-h-screen p-6 pt-16">
        <main className="w-full max-w-md flex flex-col items-center gap-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">
              사주 분석
            </h1>
            <p className="mt-3 text-lg text-zinc-600 dark:text-zinc-400">
              생년월일과 태어난 시간을 입력해주세요
            </p>
          </div>

          <div className="w-full flex flex-col gap-4">
            {/* 생년월일 */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
                  년 (양력)
                </label>
                <input
                  type="number"
                  placeholder="1990"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  className={inputClass}
                  min={1900}
                  max={2100}
                />
              </div>
              <div>
                <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
                  월
                </label>
                <input
                  type="number"
                  placeholder="1"
                  value={month}
                  onChange={(e) => setMonth(e.target.value)}
                  className={inputClass}
                  min={1}
                  max={12}
                />
              </div>
              <div>
                <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
                  일
                </label>
                <input
                  type="number"
                  placeholder="15"
                  value={day}
                  onChange={(e) => setDay(e.target.value)}
                  className={inputClass}
                  min={1}
                  max={31}
                />
              </div>
            </div>

            {/* 태어난 시간 */}
            <div>
              <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
                태어난 시간
              </label>
              <select
                value={hour}
                onChange={(e) => setHour(e.target.value)}
                className={inputClass}
              >
                <option value="">시간을 선택하세요</option>
                {HOURS.map((h) => (
                  <option key={h} value={h}>
                    {String(h).padStart(2, "0")}시 (
                    {h === 0
                      ? "자시"
                      : h <= 2
                        ? "축시"
                        : h <= 4
                          ? "인시"
                          : h <= 6
                            ? "묘시"
                            : h <= 8
                              ? "진시"
                              : h <= 10
                                ? "사시"
                                : h <= 12
                                  ? "오시"
                                  : h <= 14
                                    ? "미시"
                                    : h <= 16
                                      ? "신시"
                                      : h <= 18
                                        ? "유시"
                                        : h <= 20
                                          ? "술시"
                                          : "해시"}
                    )
                  </option>
                ))}
              </select>
            </div>

            {/* 성별 */}
            <div>
              <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
                성별
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { value: "male" as const, label: "남성" },
                  { value: "female" as const, label: "여성" },
                ].map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setGender(opt.value)}
                    className={`h-12 rounded-lg border-2 font-medium transition-all ${
                      gender === opt.value
                        ? "border-zinc-900 dark:border-zinc-100 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900"
                        : "border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:border-zinc-400 dark:hover:border-zinc-600"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {error && (
            <div className="w-full p-3 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="w-full h-12 rounded-full bg-zinc-900 text-white font-medium text-base transition-colors hover:bg-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <svg
                  className="w-5 h-5 animate-spin"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                {loadingStep || "분석 중..."}
              </>
            ) : (
              "사주 분석하기"
            )}
          </button>

          <button
            onClick={() => router.push("/")}
            className="text-sm text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
          >
            &larr; 메인으로
          </button>
        </main>
      </div>
    </AuthGuard>
  );
};

export default SajuPage;
