"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import HeroCard from "../../components/HeroCard";

interface SajuResultData {
  saju: {
    pillars: Record<
      string,
      {
        gan: string;
        zhi: string;
        ganzhi: string;
        gan_element: string;
        zhi_element: string;
        sipsin: string;
        twelve_stage: string;
      }
    >;
    elements: {
      counts: Record<string, number>;
      percentages: Record<string, number>;
      day_element: string;
    };
    yongsin: {
      strength: string;
      description: string;
      yongsin: string;
      heesin: string;
      yongsin_label: string;
      heesin_label: string;
    };
    birth_info: {
      year: number;
      month: number;
      day: number;
      hour: number;
      gender: string;
      lunar_date: string;
      animal: string;
    };
    dayun: {
      start_age: number;
      end_age: number;
      ganzhi: string;
      gan_element: string;
      zhi_element: string;
      sipsin: string;
    }[];
    scores: {
      overall_score: number;
      element_balance: { score: number };
      yongsin_strength: { score: number };
      sipsin_balance: { score: number };
      wealth: { score: number };
      love: { score: number };
      career: { score: number };
    };
  };
  analysis: {
    summary: string;
    personality: string;
    scores: { category: string; description: string; score: number }[];
    overall: string;
    fortune_advice: string[];
    lucky: { color: string; direction: string; number: string };
  };
}

const ELEMENT_COLORS: Record<string, string> = {
  목: "#22c55e",
  화: "#ef4444",
  토: "#eab308",
  금: "#a1a1aa",
  수: "#3b82f6",
};

const ELEMENT_BG: Record<string, string> = {
  목: "bg-green-500",
  화: "bg-red-500",
  토: "bg-yellow-500",
  금: "bg-zinc-400",
  수: "bg-blue-500",
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

const PILLAR_NAMES = ["년주", "월주", "일주", "시주"];
const PILLAR_KEYS = ["year", "month", "day", "hour"];

const SajuResultPage = () => {
  const [result, setResult] = useState<SajuResultData | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [hero, setHero] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);
  const reportRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const stored = sessionStorage.getItem("sajuResult");
    const heroStored = sessionStorage.getItem("heroMatch");
    if (!stored) {
      router.push("/saju");
      return;
    }
    setResult(JSON.parse(stored));
    if (heroStored) setHero(JSON.parse(heroStored));
  }, [router]);

  const handleRetry = () => {
    sessionStorage.removeItem("sajuResult");
    router.push("/saju");
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
      const imgWidth = 210;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      const pdf = new jsPDF("p", "mm", "a4");
      let yOffset = 0;
      const pageHeight = 297;
      while (yOffset < imgHeight) {
        if (yOffset > 0) pdf.addPage();
        pdf.addImage(imgData, "PNG", 0, -yOffset, imgWidth, imgHeight);
        yOffset += pageHeight;
      }
      pdf.save("사주분석_결과.pdf");
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

  const { saju, analysis } = result;
  const pillars = saju.pillars;
  const elements = saju.elements;

  return (
    <div className="flex flex-col items-center min-h-screen p-4 bg-zinc-50 dark:bg-zinc-950">
      <div
        ref={reportRef}
        className="w-full max-w-4xl bg-white dark:bg-zinc-950 rounded-2xl overflow-hidden"
      >
        {/* 위인 매칭 카드 */}
        {hero && (
          <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
            <HeroCard hero={hero} />
          </div>
        )}

        {/* 상단: 기본 정보 + 종합 점수 */}
        <div className="flex flex-col sm:flex-row gap-0 border-b border-zinc-200 dark:border-zinc-800">
          <div className="sm:w-1/3 p-6 flex flex-col items-center justify-center gap-4 bg-zinc-900 text-white">
            <div className="text-center">
              <p className="text-xs text-zinc-400">
                {saju.birth_info.lunar_date}
              </p>
              <p className="text-sm text-zinc-300 mt-1">
                {saju.birth_info.year}년 {saju.birth_info.month}월{" "}
                {saju.birth_info.day}일 {saju.birth_info.hour}시
              </p>
              <p className="text-sm text-zinc-400 mt-1">
                {saju.birth_info.animal}띠 |{" "}
                {saju.birth_info.gender === "male" ? "남" : "여"}
              </p>
            </div>
            <div className="text-center">
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-4xl font-bold">
                  {saju.scores.overall_score.toFixed(1)}
                </span>
                <span className="text-zinc-400 text-lg">/10</span>
              </div>
              <p className="text-xs text-zinc-400 mt-1">종합 점수</p>
            </div>
            {/* 미니 바 */}
            <div className="w-full space-y-1.5 px-2">
              {[
                {
                  label: "오행 균형",
                  score: saju.scores.element_balance.score,
                },
                {
                  label: "용신 강약",
                  score: saju.scores.yongsin_strength.score,
                },
                { label: "재물운", score: saju.scores.wealth.score },
                { label: "연애운", score: saju.scores.love.score },
                { label: "직업운", score: saju.scores.career.score },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-400 w-14 text-right shrink-0">
                    {item.label}
                  </span>
                  <div className="flex-1 h-1.5 bg-zinc-700 rounded-full">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${item.score * 10}%`,
                        backgroundColor: scoreColorHex(item.score),
                      }}
                    />
                  </div>
                  <span className="text-[10px] text-zinc-400 w-4">
                    {item.score.toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="sm:w-2/3 p-6 flex flex-col justify-center gap-4">
            <div>
              <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                사주 분석 결과
              </h1>
              <p className="mt-2 text-zinc-600 dark:text-zinc-400 text-sm">
                {analysis.summary}
              </p>
            </div>
            <div className="p-4 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
              <h3 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-2">
                성격 분석
              </h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                {analysis.personality}
              </p>
            </div>
          </div>
        </div>

        {/* 사주 원국 테이블 */}
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-3">
            사주 원국 (四柱)
          </h2>
          <div className="grid grid-cols-4 gap-2">
            {PILLAR_KEYS.map((key, idx) => {
              const p = pillars[key];
              return (
                <div
                  key={key}
                  className="text-center p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                >
                  <p className="text-[10px] text-zinc-400 mb-1">
                    {PILLAR_NAMES[idx]}
                  </p>
                  <div className="flex flex-col items-center gap-1">
                    <span
                      className="text-lg font-bold"
                      style={{ color: ELEMENT_COLORS[p.gan_element] }}
                    >
                      {p.gan}
                    </span>
                    <span
                      className="text-lg font-bold"
                      style={{ color: ELEMENT_COLORS[p.zhi_element] }}
                    >
                      {p.zhi}
                    </span>
                  </div>
                  <p className="text-[10px] text-zinc-500 mt-1">{p.sipsin}</p>
                  <p className="text-[10px] text-zinc-400">{p.twelve_stage}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* 오행 분포 */}
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-3">
            오행 분포
          </h2>
          <div className="flex items-end gap-2 h-24 mb-2">
            {(["목", "화", "토", "금", "수"] as const).map((elem) => (
              <div
                key={elem}
                className="flex-1 flex flex-col items-center gap-1"
              >
                <span className="text-xs text-zinc-500">
                  {elements.percentages[elem]}%
                </span>
                <div
                  className="w-full rounded-t"
                  style={{
                    height: `${Math.max(4, elements.percentages[elem] * 2)}px`,
                    backgroundColor: ELEMENT_COLORS[elem],
                  }}
                />
                <span
                  className="text-xs font-medium"
                  style={{ color: ELEMENT_COLORS[elem] }}
                >
                  {elem}
                </span>
                <span className="text-[10px] text-zinc-400">
                  {elements.counts[elem]}개
                </span>
              </div>
            ))}
          </div>
          <div className="mt-3 p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
            <p className="text-xs text-zinc-600 dark:text-zinc-400">
              <span className="font-medium">일간:</span> {elements.day_element}{" "}
              | <span className="font-medium">{saju.yongsin.strength}</span> —{" "}
              {saju.yongsin.yongsin_label} / {saju.yongsin.heesin_label}
            </p>
          </div>
        </div>

        {/* 운세 항목 */}
        {analysis.scores && analysis.scores.length > 0 && (
          <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
            <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-3">
              상세 운세
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {analysis.scores.map((item, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
                      {item.category}
                    </h3>
                    <div className="flex items-center gap-1.5">
                      <span
                        className="text-[10px] px-1.5 py-0.5 rounded-full text-white"
                        style={{ backgroundColor: scoreColorHex(item.score) }}
                      >
                        {scoreLabel(item.score)}
                      </span>
                      <span className="text-xs font-mono text-zinc-400">
                        {item.score.toFixed(1)}/10
                      </span>
                    </div>
                  </div>
                  <div className="w-full h-1 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-2">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${item.score * 10}%`,
                        backgroundColor: scoreColorHex(item.score),
                      }}
                    />
                  </div>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 대운 흐름 */}
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-3">
            대운 흐름
          </h2>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {saju.dayun.map((d, idx) => (
              <div
                key={idx}
                className="shrink-0 text-center p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 min-w-[72px]"
              >
                <p className="text-[10px] text-zinc-400">
                  {d.start_age}~{d.end_age}세
                </p>
                <p
                  className="text-sm font-bold mt-1"
                  style={{ color: ELEMENT_COLORS[d.gan_element] }}
                >
                  {d.ganzhi}
                </p>
                <p className="text-[10px] text-zinc-500 mt-1">{d.sipsin}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 종합 분석 */}
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-2">
            종합 분석
          </h2>
          <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
            {analysis.overall}
          </p>
        </div>

        {/* 조언 + 행운 */}
        <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {analysis.fortune_advice && analysis.fortune_advice.length > 0 && (
            <div className="p-4 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
              <h3 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-2">
                실천 조언
              </h3>
              <ul className="space-y-1.5">
                {analysis.fortune_advice.map((advice, idx) => (
                  <li
                    key={idx}
                    className="text-xs text-zinc-600 dark:text-zinc-400 flex gap-2"
                  >
                    <span className="shrink-0 text-zinc-400">{idx + 1}.</span>
                    {advice}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {analysis.lucky && (
            <div className="p-4 rounded-lg bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800">
              <h3 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-2">
                행운 정보
              </h3>
              <div className="space-y-1.5 text-xs text-zinc-600 dark:text-zinc-400">
                <p>길한 색상: {analysis.lucky.color}</p>
                <p>길한 방향: {analysis.lucky.direction}</p>
                <p>행운의 숫자: {analysis.lucky.number}</p>
              </div>
            </div>
          )}
        </div>

        {/* 푸터 */}
        <div className="px-6 pb-4 text-center">
          <p className="text-[10px] text-zinc-300 dark:text-zinc-600">
            Physiognomy AI - 본 결과는 전통 명리학에 기반한 재미 목적의
            분석이며, 과학적 근거가 아닙니다.
          </p>
        </div>
      </div>

      {/* 버튼 */}
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

export default SajuResultPage;
