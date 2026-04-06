"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "../hooks/useAuth";

const TODAY_CATEGORY = {
  value: "오늘의 운세",
  label: "오늘의 운세",
  description: "오늘 하루의 흐름",
};

const CATEGORIES = [
  { value: "연애", label: "연애운", description: "사랑과 인연의 흐름" },
  { value: "재물", label: "재물운", description: "재물과 금전의 흐름" },
  { value: "직업", label: "직업운", description: "직업과 커리어의 흐름" },
  { value: "건강", label: "건강운", description: "건강과 활력의 흐름" },
];

const TarotPage = () => {
  const [category, setCategory] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { getAccessToken } = useAuth();

  const handleSubmit = useCallback(async () => {
    if (!category) {
      setError("카테고리를 선택해주세요.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setLoadingStep("카드를 섞고 있어요...");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const token = await getAccessToken();
      const res = await fetch(`${apiUrl}/api/tarot`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          category,
          stream: true,
          turnstile_token: "",
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
      let tarotData: Record<string, unknown> | null = null;

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
              tarotData = msg.data;
              if (msg.hero)
                sessionStorage.setItem("heroMatch", JSON.stringify(msg.hero));
              setLoadingStep("타로를 해석하고 있어요...");
            } else if (msg.type === "chunk") {
              setLoadingStep("타로 분석을 작성하고 있어요...");
            } else if (msg.type === "done") {
              sessionStorage.setItem(
                "tarotResult",
                JSON.stringify({
                  spread: tarotData
                    ? (tarotData as Record<string, unknown>).spread
                    : null,
                  scores: tarotData
                    ? (tarotData as Record<string, unknown>).scores
                    : null,
                  analysis: msg.data,
                }),
              );
              router.push("/tarot/result");
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
  }, [category, router]);

  return (
    <div className="flex flex-col items-center justify-center flex-1 p-6">
      <main className="w-full flex flex-col items-center gap-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">
            타로 분석
          </h1>
          <p className="mt-3 text-lg text-zinc-600 dark:text-zinc-400">
            궁금한 운세 카테고리를 선택하세요
          </p>
        </div>

        <div className="w-full flex flex-col gap-3">
          <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
            카테고리
          </label>
          {/* 오늘의 운세 — 전체 너비 */}
          <button
            onClick={() => setCategory(TODAY_CATEGORY.value)}
            className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
              category === TODAY_CATEGORY.value
                ? "border-zinc-900 dark:border-zinc-100 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900"
                : "border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:border-zinc-400 dark:hover:border-zinc-600"
            }`}
          >
            <p className="font-semibold text-sm">{TODAY_CATEGORY.label}</p>
            <p
              className={`text-xs mt-0.5 ${
                category === TODAY_CATEGORY.value
                  ? "text-zinc-300 dark:text-zinc-500"
                  : "text-zinc-400 dark:text-zinc-500"
              }`}
            >
              {TODAY_CATEGORY.description}
            </p>
          </button>
          {/* 나머지 4개 — 2x2 그리드 */}
          <div className="grid grid-cols-2 gap-3">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setCategory(cat.value)}
                className={`p-4 rounded-xl border-2 text-left transition-all ${
                  category === cat.value
                    ? "border-zinc-900 dark:border-zinc-100 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900"
                    : "border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:border-zinc-400 dark:hover:border-zinc-600"
                }`}
              >
                <p className="font-semibold text-sm">{cat.label}</p>
                <p
                  className={`text-xs mt-0.5 ${
                    category === cat.value
                      ? "text-zinc-300 dark:text-zinc-500"
                      : "text-zinc-400 dark:text-zinc-500"
                  }`}
                >
                  {cat.description}
                </p>
              </button>
            ))}
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
            "카드 뽑기"
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
  );
};

export default TarotPage;
