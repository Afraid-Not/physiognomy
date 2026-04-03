"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";

interface AnalysisResult {
  summary: string;
  features: {
    category: string;
    description: string;
    score: number;
  }[];
  overall: string;
}

const scoreColor = (score: number) => {
  if (score >= 8) return "bg-emerald-500";
  if (score >= 6) return "bg-blue-500";
  if (score >= 4) return "bg-amber-500";
  return "bg-red-400";
};

const scoreColorHex = (score: number) => {
  if (score >= 8) return "#10b981";
  if (score >= 6) return "#3b82f6";
  if (score >= 4) return "#f59e0b";
  return "#f87171";
};

const scoreLabel = (score: number) => {
  if (score >= 9) return "최상";
  if (score >= 7) return "좋음";
  if (score >= 5) return "보통";
  return "주의";
};

const ResultPage = () => {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const reportRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const stored = sessionStorage.getItem("analysisResult");
    const image = sessionStorage.getItem("uploadedImage");
    if (!stored) {
      router.push("/");
      return;
    }
    setResult(JSON.parse(stored));
    if (image) setUploadedImage(image);
  }, [router]);

  const handleRetry = () => {
    sessionStorage.removeItem("analysisResult");
    sessionStorage.removeItem("uploadedImage");
    router.push("/face");
  };

  const handleSavePdf = async () => {
    if (!reportRef.current) return;
    setIsSaving(true);

    try {
      const html2canvas = (await import("html2canvas-pro")).default;
      const { jsPDF } = await import("jspdf");

      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: "#ffffff",
      });

      const imgData = canvas.toDataURL("image/png");
      const imgWidth = 210; // A4 width mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      const pdf = new jsPDF("p", "mm", "a4");
      let yOffset = 0;
      const pageHeight = 297; // A4 height mm

      // 여러 페이지 처리
      while (yOffset < imgHeight) {
        if (yOffset > 0) pdf.addPage();
        pdf.addImage(imgData, "PNG", 0, -yOffset, imgWidth, imgHeight);
        yOffset += pageHeight;
      }

      pdf.save("관상분석_결과.pdf");
    } catch (err) {
      console.error("PDF 저장 실패:", err);
    } finally {
      setIsSaving(false);
    }
  };

  if (!result) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-3">
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
          <p className="text-zinc-500">결과를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  const avgScore =
    result.features.reduce((sum, f) => sum + f.score, 0) /
    result.features.length;

  // 부위별 결과를 2열 그리드로 분할
  const leftFeatures = result.features.filter((_, i) => i % 2 === 0);
  const rightFeatures = result.features.filter((_, i) => i % 2 === 1);

  return (
    <div className="flex flex-col items-center min-h-screen p-4 bg-zinc-50 dark:bg-zinc-950">
      {/* PDF 캡처 영역 */}
      <div
        ref={reportRef}
        className="w-full max-w-4xl bg-white dark:bg-zinc-950 rounded-2xl overflow-hidden"
      >
        {/* 상단: 사진(좌) + 요약(우) */}
        <div className="flex flex-col sm:flex-row gap-0 border-b border-zinc-200 dark:border-zinc-800">
          {/* 좌: 사진 + 종합점수 */}
          <div className="sm:w-1/3 p-6 flex flex-col items-center justify-center gap-4 bg-zinc-900 dark:bg-zinc-900 text-white">
            {uploadedImage && (
              <div className="w-28 h-28 rounded-full overflow-hidden border-4 border-zinc-600">
                <img
                  src={uploadedImage}
                  alt="분석된 사진"
                  className="w-full h-full object-cover"
                />
              </div>
            )}
            <div className="text-center">
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-4xl font-bold">
                  {avgScore.toFixed(1)}
                </span>
                <span className="text-zinc-400 text-lg">/10</span>
              </div>
              <p className="text-xs text-zinc-400 mt-1">종합 점수</p>
            </div>
            {/* 미니 바 차트 */}
            <div className="w-full space-y-1.5 px-2">
              {result.features.map((f, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-400 w-16 text-right shrink-0 whitespace-nowrap">
                    {f.category.split(" - ")[0]}
                  </span>
                  <div className="flex-1 h-1.5 bg-zinc-700 rounded-full">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${f.score * 10}%`,
                        backgroundColor: scoreColorHex(f.score),
                      }}
                    />
                  </div>
                  <span className="text-[10px] text-zinc-400 w-4">
                    {f.score.toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* 우: 요약 + 종합 분석 */}
          <div className="sm:w-2/3 p-6 flex flex-col justify-center gap-4">
            <div>
              <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                관상 분석 결과
              </h1>
              <p className="mt-2 text-zinc-600 dark:text-zinc-400 text-sm">
                {result.summary}
              </p>
            </div>
            <div className="p-4 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
              <h3 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-2">
                종합 분석
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                {result.overall}
              </p>
            </div>
          </div>
        </div>

        {/* 하단: 부위별 결과 2열 그리드 */}
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {result.features.map((feature, idx) => (
              <div
                key={idx}
                className="p-4 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 whitespace-nowrap shrink-0">
                    {feature.category}
                  </h3>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span
                      className="text-[10px] px-1.5 py-0.5 rounded-full text-white"
                      style={{ backgroundColor: scoreColorHex(feature.score) }}
                    >
                      {scoreLabel(feature.score)}
                    </span>
                    <span className="text-xs font-mono text-zinc-400">
                      {feature.score.toFixed(1)}/10
                    </span>
                  </div>
                </div>
                <div className="w-full h-1 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-2">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${feature.score * 10}%`,
                      backgroundColor: scoreColorHex(feature.score),
                    }}
                  />
                </div>
                <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 푸터 */}
        <div className="px-6 pb-4 text-center">
          <p className="text-[10px] text-zinc-300 dark:text-zinc-600">
            Physiognomy AI - 본 결과는 전통 관상학에 기반한 재미 목적의
            분석이며, 과학적 근거가 아닙니다.
          </p>
        </div>
      </div>

      {/* 버튼들 (PDF 캡처 영역 밖) */}
      <div className="w-full max-w-4xl flex gap-3 mt-6">
        <button
          onClick={handleSavePdf}
          disabled={isSaving}
          className="flex-1 h-12 rounded-full bg-zinc-900 text-white font-medium transition-colors hover:bg-zinc-700 disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300 flex items-center justify-center gap-2"
        >
          {isSaving ? (
            <>
              <svg
                className="w-4 h-4 animate-spin"
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
              저장 중...
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              PDF 저장
            </>
          )}
        </button>
        <button
          onClick={handleRetry}
          className="flex-1 h-12 rounded-full border-2 border-zinc-900 dark:border-zinc-100 text-zinc-900 dark:text-zinc-100 font-medium transition-colors hover:bg-zinc-900 hover:text-white dark:hover:bg-zinc-100 dark:hover:text-zinc-900"
        >
          다시 분석하기
        </button>
      </div>
    </div>
  );
};

export default ResultPage;
