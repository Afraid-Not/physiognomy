"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import AuthGuard from "../../../components/AuthGuard";

import { useAuth } from "../../../hooks/useAuth";

interface HistoryDetail {
  id: string;
  type: string;
  created_at: string;
  input_data: Record<string, unknown>;
  result_data: Record<string, unknown>;
  image_signed_url?: string;
}

const TYPE_LABELS: Record<string, string> = {
  face: "관상 분석",
  saju: "사주 분석",
  combined: "종합 분석",
};

const HistoryDetailPage = () => {
  const [data, setData] = useState<HistoryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getAccessToken } = useAuth();
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const token = await getAccessToken();
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/history/${id}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!res.ok) throw new Error("이력을 불러올 수 없습니다.");
        const result = await res.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "오류가 발생했습니다.");
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchDetail();
  }, [id, getAccessToken]);

  const handleRestore = () => {
    if (!data) return;
    // 타입별로 sessionStorage에 저장 후 결과 페이지로 이동
    if (data.type === "face") {
      sessionStorage.setItem(
        "analysisResult",
        JSON.stringify(data.result_data),
      );
      if (data.image_signed_url)
        sessionStorage.setItem("uploadedImage", data.image_signed_url);
      router.push("/face/result");
    } else if (data.type === "saju") {
      sessionStorage.setItem("sajuResult", JSON.stringify(data.result_data));
      router.push("/saju/result");
    } else if (data.type === "combined") {
      // combined의 result_data에서 필요한 구조 복원
      const rd = data.result_data as Record<string, unknown>;
      sessionStorage.setItem(
        "combinedResult",
        JSON.stringify({
          classified: {
            face: rd.face ? { features: [] } : { features: [] },
            saju: rd.saju_scores ? { ...rd, scores: rd.saju_scores } : rd,
          },
          analysis: rd.combined ?? rd,
        }),
      );
      if (data.image_signed_url)
        sessionStorage.setItem("uploadedImage", data.image_signed_url);
      router.push("/combined/result");
    }
  };

  return (
    <AuthGuard>
      <div className="flex flex-col items-center flex-1 p-4">
        <div className="w-full max-w-2xl">
          <button
            onClick={() => router.push("/mypage")}
            className="text-sm text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors mb-4"
          >
            &larr; 마이페이지로
          </button>

          {loading && (
            <div className="flex justify-center py-20">
              <svg
                className="w-8 h-8 animate-spin text-zinc-400"
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
            </div>
          )}

          {error && (
            <div className="p-4 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          {data && (
            <div className="p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
                    {TYPE_LABELS[data.type] ?? data.type}
                  </h1>
                  <p className="text-xs text-zinc-400 mt-1">
                    {new Date(data.created_at).toLocaleDateString("ko-KR", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
                <button
                  onClick={handleRestore}
                  className="px-4 py-2 rounded-full bg-zinc-900 text-white text-sm font-medium hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300 transition-colors"
                >
                  결과 보기
                </button>
              </div>

              {data.image_signed_url && (
                <div className="mb-4">
                  <img
                    src={data.image_signed_url}
                    alt="분석 사진"
                    className="w-32 h-32 rounded-lg object-cover"
                  />
                </div>
              )}

              {data.input_data && Object.keys(data.input_data).length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100 mb-2">
                    입력 정보
                  </h3>
                  <div className="text-xs text-zinc-500 dark:text-zinc-400 space-y-1">
                    {Object.entries(data.input_data).map(([k, v]) => (
                      <p key={k}>
                        {k}: {String(v)}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
};

export default HistoryDetailPage;
