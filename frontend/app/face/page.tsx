"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import AuthGuard from "../components/AuthGuard";

import { useAuth } from "../hooks/useAuth";

const FacePage = () => {
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
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

  const handleUpload = useCallback(async () => {
    if (!file) {
      setError("파일을 선택해주세요.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setLoadingStep("얼굴을 분석하고 있어요...");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const token = await getAccessToken();
      const res = await fetch(`${apiUrl}/api/analyze?stream=true`, {
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
              if (msg.hero)
                sessionStorage.setItem("heroMatch", JSON.stringify(msg.hero));
              setLoadingStep("관상 지식을 찾고 있어요...");
            } else if (msg.type === "chunk") {
              setLoadingStep("관상 분석을 작성하고 있어요...");
            } else if (msg.type === "done") {
              sessionStorage.setItem(
                "analysisResult",
                JSON.stringify(msg.data),
              );
              if (preview) sessionStorage.setItem("uploadedImage", preview);
              router.push("/face/result");
              return;
            } else if (msg.type === "error") {
              throw new Error(msg.data);
            }
          } catch {
            // JSON parse error for incomplete chunks - ignore
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
  }, [file, preview, router, getAccessToken]);

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

  return (
    <AuthGuard>
      <div className="flex flex-col items-center justify-center flex-1 p-6">
        <main className="w-full flex flex-col items-center gap-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">
              관상 분석
            </h1>
            <p className="mt-3 text-lg text-zinc-600 dark:text-zinc-400">
              사진을 업로드하면 AI가 관상을 분석해드립니다
            </p>
            <p className="mt-1 text-xs text-zinc-400 dark:text-zinc-500">
              정면 사진이 가장 정확하며, 얼굴 각도에 따라 결과가 다를 수
              있습니다
            </p>
          </div>

          <div
            className="w-full aspect-square max-w-sm border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-2xl flex items-center justify-center overflow-hidden cursor-pointer hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors bg-white dark:bg-zinc-900"
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {preview ? (
              <img
                src={preview}
                alt="업로드된 사진 미리보기"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="flex flex-col items-center gap-3 text-zinc-400 dark:text-zinc-500">
                <svg
                  className="w-12 h-12"
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
                <p className="text-sm">클릭하거나 사진을 드래그하세요</p>
                <p className="text-xs text-zinc-300 dark:text-zinc-600">
                  정면 사진을 권장합니다
                </p>
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

          {error && (
            <div className="w-full max-w-sm p-3 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || isLoading}
            className="w-full max-w-sm h-12 rounded-full bg-zinc-900 text-white font-medium text-base transition-colors hover:bg-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300 flex items-center justify-center gap-2"
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
              "관상 분석하기"
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

export default FacePage;
