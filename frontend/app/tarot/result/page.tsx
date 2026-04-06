"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import HeroCard from "../../components/HeroCard";

interface CardInterpretation {
  position: string;
  card_name: string;
  description: string;
  score: number;
}

interface TarotResultData {
  spread: {
    category: string;
    cards: {
      position: string;
      card_number: number;
      card_name: string;
      card_name_en: string;
      is_reversed: boolean;
      upright_keywords: string;
      reversed_keywords: string;
      element: string;
      meaning: string;
    }[];
  };
  scores: {
    category: string;
    overall_score: number;
    card_scores: {
      position: string;
      card_name: string;
      is_reversed: boolean;
      base_score: number;
      adjusted_score: number;
    }[];
    fortune_scores: {
      luck: number;
      timing: number;
      energy: number;
    };
  };
  analysis: {
    summary: string;
    card_interpretations: CardInterpretation[];
    overall: string;
    fortune_advice: string[];
    lucky: { color: string; direction: string; number: string };
    overall_score?: number;
  };
}

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

const ELEMENT_LABELS: Record<string, string> = {
  풍: "Air",
  화: "Fire",
  수: "Water",
  토: "Earth",
};

const TarotResultPage = () => {
  const [result, setResult] = useState<TarotResultData | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [hero, setHero] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);
  const reportRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const stored = sessionStorage.getItem("tarotResult");
    const heroStored = sessionStorage.getItem("heroMatch");
    if (!stored) {
      router.push("/tarot");
      return;
    }
    setResult(JSON.parse(stored));
    if (heroStored) setHero(JSON.parse(heroStored));
  }, [router]);

  const handleRetry = () => {
    sessionStorage.removeItem("tarotResult");
    sessionStorage.removeItem("heroMatch");
    router.push("/tarot");
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
      pdf.save("타로분석_결과.pdf");
    } catch (err) {
      console.error("PDF 저장 실패:", err);
    } finally {
      setIsSaving(false);
    }
  };

  if (!result) {
    return (
      <div className="flex items-center justify-center flex-1">
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

  const { spread, scores, analysis } = result;

  return (
    <div className="flex flex-col items-center flex-1 p-4">
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

        {/* 상단: 카테고리 + 종합 점수 */}
        <div className="flex flex-col sm:flex-row gap-0 border-b border-zinc-200 dark:border-zinc-800">
          <div className="sm:w-1/3 p-6 flex flex-col items-center justify-center gap-4 bg-zinc-900 text-white">
            <div className="text-center">
              <p className="text-xs text-zinc-400">타로 카테고리</p>
              <p className="text-lg font-bold mt-1">{spread.category}</p>
            </div>
            <div className="text-center">
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-4xl font-bold">
                  {scores.overall_score.toFixed(1)}
                </span>
                <span className="text-zinc-400 text-lg">/10</span>
              </div>
              <p className="text-xs text-zinc-400 mt-1">종합 점수</p>
            </div>
            {/* 미니 바 */}
            <div className="w-full space-y-1.5 px-2">
              {[
                { label: "행운", score: scores.fortune_scores.luck },
                { label: "타이밍", score: scores.fortune_scores.timing },
                { label: "에너지", score: scores.fortune_scores.energy },
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
                타로 분석 결과
              </h1>
              <p className="mt-2 text-zinc-800 dark:text-zinc-400 text-sm">
                {analysis.summary}
              </p>
            </div>
          </div>
        </div>

        {/* 쓰리카드 스프레드 */}
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-3">
            쓰리카드 스프레드
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {spread.cards.map((card, idx) => {
              const cardScore = scores.card_scores[idx];
              return (
                <div
                  key={card.position}
                  className={`text-center p-4 rounded-xl border-2 ${
                    card.is_reversed
                      ? "border-zinc-400 dark:border-zinc-600 bg-zinc-50 dark:bg-zinc-900"
                      : "border-zinc-900 dark:border-zinc-200 bg-white dark:bg-zinc-900"
                  }`}
                >
                  <p className="text-[10px] text-zinc-400 mb-2">
                    {card.position}
                  </p>
                  <p className="text-xs text-zinc-500 mb-1">
                    {card.card_number}번
                  </p>
                  <p
                    className={`text-lg font-bold ${
                      card.is_reversed
                        ? "text-zinc-500 dark:text-zinc-400"
                        : "text-zinc-900 dark:text-zinc-100"
                    }`}
                  >
                    {card.card_name}
                  </p>
                  <p className="text-[10px] text-zinc-400 mt-0.5">
                    {card.card_name_en}
                  </p>
                  <div className="mt-2 flex items-center justify-center gap-1">
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full ${
                        card.is_reversed
                          ? "bg-zinc-200 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300"
                          : "bg-zinc-900 dark:bg-zinc-200 text-white dark:text-zinc-900"
                      }`}
                    >
                      {card.is_reversed ? "역방향" : "정방향"}
                    </span>
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-2">
                    {card.element} (
                    {ELEMENT_LABELS[card.element] ?? card.element})
                  </p>
                  {cardScore && (
                    <div className="mt-2">
                      <span
                        className="text-xs font-mono"
                        style={{
                          color: scoreColorHex(cardScore.adjusted_score),
                        }}
                      >
                        {cardScore.adjusted_score.toFixed(1)}/10
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* 카드별 해석 */}
        {analysis.card_interpretations &&
          analysis.card_interpretations.length > 0 && (
            <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
              <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-3">
                카드별 해석
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {analysis.card_interpretations.map(
                  (interp: CardInterpretation, idx: number) => (
                    <div
                      key={idx}
                      className="p-4 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                    >
                      <div className="text-center mb-2">
                        <p className="text-[10px] text-zinc-400">
                          {interp.position}
                        </p>
                        <h3 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mt-0.5">
                          {interp.card_name
                            .replace(/\s*\(.*?\)/g, "")
                            .replace(/\s*(역방향|정방향)/g, "")
                            .trim()}
                        </h3>
                        {spread.cards[idx] && (
                          <span
                            className={`inline-block text-[10px] px-2 py-0.5 rounded-full mt-1 ${
                              spread.cards[idx].is_reversed
                                ? "bg-zinc-200 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300"
                                : "bg-zinc-900 dark:bg-zinc-200 text-white dark:text-zinc-900"
                            }`}
                          >
                            {spread.cards[idx].is_reversed
                              ? "역방향"
                              : "정방향"}
                          </span>
                        )}
                        <div className="flex items-center justify-center gap-1.5 mt-1.5">
                          <span
                            className="text-[10px] px-1.5 py-0.5 rounded-full text-white"
                            style={{
                              backgroundColor: scoreColorHex(interp.score),
                            }}
                          >
                            {scoreLabel(interp.score)}
                          </span>
                          <span className="text-xs font-mono text-zinc-400">
                            {interp.score.toFixed(1)}
                          </span>
                        </div>
                      </div>
                      <div className="w-full h-1 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-2">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${interp.score * 10}%`,
                            backgroundColor: scoreColorHex(interp.score),
                          }}
                        />
                      </div>
                      <p className="text-xs text-zinc-800 dark:text-zinc-400 leading-relaxed">
                        {interp.description}
                      </p>
                    </div>
                  ),
                )}
              </div>
            </div>
          )}

        {/* 종합 분석 */}
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 mb-2">
            종합 분석
          </h2>
          <p className="text-sm text-zinc-800 dark:text-zinc-400 leading-relaxed">
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
                {analysis.fortune_advice.map((advice: string, idx: number) => (
                  <li
                    key={idx}
                    className="text-xs text-zinc-800 dark:text-zinc-400 flex gap-2"
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
              <div className="space-y-1.5 text-xs text-zinc-800 dark:text-zinc-400">
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
            Physiognomy AI - 본 결과는 재미 목적의 타로 해석이며, 과학적 근거가
            아닙니다.
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
          다시 뽑기
        </button>
      </div>

      <p className="text-xs text-zinc-400 dark:text-zinc-500 text-center mt-4 pb-2">
        본 결과는 재미로 보는 타로이며, 과학적 근거가 없습니다. 결과에 의미를
        두지 마세요.
      </p>
    </div>
  );
};

export default TarotResultPage;
