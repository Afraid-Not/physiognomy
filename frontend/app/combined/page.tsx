"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Turnstile } from "@marsidev/react-turnstile";

import { useAuth } from "../hooks/useAuth";

const HOURS = Array.from({ length: 24 }, (_, i) => i);

const CombinedPage = () => {
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [hour, setHour] = useState("");
  const [gender, setGender] = useState<"male" | "female" | "">("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const turnstileRef = useRef<any>(null);
  const router = useRouter();
  const { getAccessToken } = useAuth();

  const handleFileSelect = useCallback((selected: File) => {
    if (!selected.type.startsWith("image/")) {
      setError("이미지 파일만 업로드 가능합니다.");
      return;
    }
    setError(null);
    setFile(selected);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result as string);
    reader.readAsDataURL(selected);
  }, []);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files?.[0];
      if (selected) handleFileSelect(selected);
    },
    [handleFileSelect],
  );

  const handleSubmit = useCallback(async () => {
    if (!file) {
      setError("사진을 선택해주세요.");
      return;
    }
    if (!year || !month || !day || hour === "" || !gender) {
      setError("모든 항목을 입력해주세요.");
      return;
    }
    if (!turnstileToken) {
      setError("캡챠 인증을 완료해주세요.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setLoadingStep("얼굴과 사주를 분석하고 있어요...");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("birth_year", year);
      formData.append("birth_month", month);
      formData.append("birth_day", day);
      formData.append("birth_hour", hour);
      formData.append("birth_minute", "0");
      formData.append("gender", gender);
      formData.append("stream", "true");
      formData.append("turnstile_token", turnstileToken);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const token = await getAccessToken();
      const res = await fetch(`${apiUrl}/api/combined`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail ?? `분석 실패 (${res.status})`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("스트리밍을 시작할 수 없습니다.");

      const decoder = new TextDecoder();
      let buffer = "";
      let classifiedData: Record<string, unknown> | null = null;

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
              classifiedData = msg.data;
              if (msg.hero)
                sessionStorage.setItem("heroMatch", JSON.stringify(msg.hero));
              setLoadingStep("종합 운세를 작성하고 있어요...");
            } else if (msg.type === "chunk") {
              setLoadingStep("종합 분석을 작성하고 있어요...");
            } else if (msg.type === "done") {
              sessionStorage.setItem(
                "combinedResult",
                JSON.stringify({
                  classified: classifiedData,
                  analysis: msg.data,
                }),
              );
              if (preview) sessionStorage.setItem("uploadedImage", preview);
              router.push("/combined/result");
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
      setTurnstileToken(null);
      turnstileRef.current?.reset();
    }
  }, [
    file,
    year,
    month,
    day,
    hour,
    gender,
    preview,
    router,
    getAccessToken,
    turnstileToken,
  ]);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFileSelect(dropped);
    },
    [handleFileSelect],
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  }, []);

  const inputClass =
    "w-full h-12 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:focus:ring-zinc-500 transition-shadow";

  return (
    <div className="flex flex-col items-center justify-center flex-1 p-6">
      <main className="w-full flex flex-col items-center gap-6">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">
            종합 분석
          </h1>
          <p className="mt-3 text-lg text-zinc-600 dark:text-zinc-400">
            관상 + 사주를 합쳐 종합 운세를 봅니다
          </p>
          <p className="mt-1 text-xs text-zinc-400 dark:text-zinc-500">
            정면 사진이 가장 정확하며, 얼굴 각도에 따라 결과가 다를 수 있습니다
          </p>
        </div>

        {/* 사진 업로드 */}
        <div
          className="w-full aspect-[4/3] max-w-sm border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-2xl flex items-center justify-center overflow-hidden cursor-pointer hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors bg-white dark:bg-zinc-900"
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {preview ? (
            <img
              src={preview}
              alt="미리보기"
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex flex-col items-center gap-2 text-zinc-400 dark:text-zinc-500">
              <svg
                className="w-10 h-10"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M12 16v-8m0 0l-3 3m3-3l3 3M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm">정면 사진을 업로드하세요</p>
            </div>
          )}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* 생년월일 */}
        <div className="w-full flex flex-col gap-4">
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

        <Turnstile
          ref={turnstileRef}
          siteKey={process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY ?? ""}
          onSuccess={setTurnstileToken}
          onExpire={() => setTurnstileToken(null)}
          options={{ theme: "light", size: "normal" }}
        />

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
            "종합 분석하기"
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

export default CombinedPage;
