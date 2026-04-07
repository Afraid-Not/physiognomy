"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

interface SignInfo {
  sign_ko: string;
  sign_en: string;
  symbol: string;
  element: string;
  modality: string;
  ruler: string;
  date_range: string;
  degree: number;
}

interface ZodiacData {
  sun: SignInfo;
  moon: SignInfo;
  ascendant: SignInfo;
}

interface ZodiacScores {
  personality_scores: Record<string, number>;
  aptitude_scores: Record<string, number>;
  overall_score: number;
  top_personality: { trait: string; score: number }[];
  top_aptitude: { trait: string; score: number }[];
}

interface ZodiacAnalysis {
  summary: string;
  sun_description: string;
  moon_description: string;
  ascendant_description: string;
  synergy: string;
  personality_description: string;
  aptitude_description: string;
  overall: string;
  fortune_advice: string[];
  lucky: { color: string; direction: string; number: string };
  overall_score?: number;
}

interface HeroMatch {
  name: string;
  title: string;
  description: string;
  tags: string[];
  match_score: number;
  common_traits: string[];
}

const scoreColor = (score: number) => {
  if (score >= 8) return "#10b981";
  if (score >= 6) return "#3b82f6";
  if (score >= 4) return "#f59e0b";
  return "#f87171";
};

const ELEMENT_COLORS: Record<string, string> = {
  불: "text-red-500 dark:text-red-400",
  흙: "text-amber-600 dark:text-amber-500",
  바람: "text-sky-500 dark:text-sky-400",
  물: "text-blue-500 dark:text-blue-400",
};

const ELEMENT_BG: Record<string, string> = {
  불: "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800",
  흙: "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800",
  바람: "bg-sky-50 dark:bg-sky-950/30 border-sky-200 dark:border-sky-800",
  물: "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800",
};

const ScoreBar = ({ label, score }: { label: string; score: number }) => (
  <div>
    <div className="flex justify-between items-center mb-1">
      <span className="text-xs text-zinc-600 dark:text-zinc-400">{label}</span>
      <span
        className="text-xs font-semibold"
        style={{ color: scoreColor(score) }}
      >
        {score.toFixed(1)}
      </span>
    </div>
    <div className="h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all"
        style={{
          width: `${(score / 10) * 100}%`,
          backgroundColor: scoreColor(score),
        }}
      />
    </div>
  </div>
);

const SignCard = ({
  label,
  emoji,
  info,
  description,
}: {
  label: string;
  emoji: string;
  info: SignInfo;
  description: string;
}) => (
  <div
    className={`rounded-2xl border p-4 flex flex-col gap-2 ${ELEMENT_BG[info.element] ?? "bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800"}`}
  >
    <div className="flex items-center gap-2">
      <span className="text-2xl">{emoji}</span>
      <div>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">
          {label}
        </p>
        <p className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
          {info.symbol} {info.sign_ko}
        </p>
      </div>
      <span
        className={`ml-auto text-xs font-semibold px-2 py-0.5 rounded-full bg-white/60 dark:bg-black/20 ${ELEMENT_COLORS[info.element] ?? ""}`}
      >
        {info.element}
      </span>
    </div>
    <div className="flex gap-3 text-xs text-zinc-500 dark:text-zinc-400">
      <span>{info.modality}</span>
      <span>·</span>
      <span>지배행성: {info.ruler}</span>
      {info.date_range && (
        <>
          <span>·</span>
          <span>{info.date_range}</span>
        </>
      )}
    </div>
    <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
      {description}
    </p>
  </div>
);

export default function ZodiacResultPage() {
  const router = useRouter();
  const reportRef = useRef<HTMLDivElement>(null);
  const [result, setResult] = useState<{
    classified: { zodiac: ZodiacData; scores: ZodiacScores } | null;
    analysis: ZodiacAnalysis | null;
  } | null>(null);
  const [hero, setHero] = useState<HeroMatch | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("zodiacResult");
    const heroRaw = sessionStorage.getItem("heroMatch");
    if (!raw) {
      router.push("/zodiac");
      return;
    }
    setResult(JSON.parse(raw));
    if (heroRaw) setHero(JSON.parse(heroRaw));
  }, [router]);

  if (!result?.classified || !result?.analysis) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 p-6">
        <p className="text-zinc-500">분석 결과를 불러오는 중...</p>
      </div>
    );
  }

  const { zodiac, scores } = result.classified;
  const analysis = result.analysis;
  const overallScore = analysis.overall_score ?? scores.overall_score;

  const handleSavePdf = async () => {
    const { default: html2canvas } = await import("html2canvas-pro");
    const { default: jsPDF } = await import("jspdf");
    if (!reportRef.current) return;
    const canvas = await html2canvas(reportRef.current, { scale: 2 });
    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "px",
      format: [canvas.width / 2, canvas.height / 2],
    });
    pdf.addImage(
      canvas.toDataURL("image/png"),
      "PNG",
      0,
      0,
      canvas.width / 2,
      canvas.height / 2,
    );
    pdf.save("별자리_분석.pdf");
  };

  return (
    <div className="flex flex-col items-center justify-center flex-1 p-4">
      <div ref={reportRef} className="w-full flex flex-col gap-4">
        {/* 헤더 */}
        <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-5">
          <div className="flex items-center gap-3">
            <div className="text-3xl">✨</div>
            <div className="flex-1">
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                종합 점수
              </p>
              <div className="flex items-center gap-2">
                <span
                  className="text-2xl font-bold"
                  style={{ color: scoreColor(overallScore) }}
                >
                  {overallScore.toFixed(1)}
                </span>
                <span className="text-zinc-400 dark:text-zinc-500">/10</span>
              </div>
            </div>
          </div>
          <p className="mt-3 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed font-medium">
            {analysis.summary}
          </p>
        </div>

        {/* 위인 매칭 */}
        {hero && (
          <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-2 font-medium">
              나와 닮은 한국 위인
            </p>
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 rounded-xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-xl">
                👑
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-bold text-zinc-900 dark:text-zinc-100">
                    {hero.name}
                  </p>
                  <span className="text-xs text-zinc-500 dark:text-zinc-400">
                    {hero.title}
                  </span>
                  <span
                    className="ml-auto text-xs font-semibold"
                    style={{ color: scoreColor(hero.match_score / 10) }}
                  >
                    {hero.match_score}점
                  </span>
                </div>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 leading-relaxed">
                  {hero.description}
                </p>
                {hero.common_traits.length > 0 && (
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {hero.common_traits.map((t) => (
                      <span
                        key={t}
                        className="px-2 py-0.5 text-xs rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 3궁 카드 */}
        <div className="flex flex-col gap-3">
          <SignCard
            label="태양궁 (Sun Sign) — 핵심 자아"
            emoji="☀️"
            info={zodiac.sun}
            description={analysis.sun_description}
          />
          <SignCard
            label="달궁 (Moon Sign) — 내면 감정"
            emoji="🌙"
            info={zodiac.moon}
            description={analysis.moon_description}
          />
          <SignCard
            label="상승궁 (Rising Sign) — 사회적 이미지"
            emoji="⬆️"
            info={zodiac.ascendant}
            description={analysis.ascendant_description}
          />
        </div>

        {/* 3궁 시너지 */}
        {analysis.synergy && (
          <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
            <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
              세 궁의 시너지
            </p>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
              {analysis.synergy}
            </p>
          </div>
        )}

        {/* 성격 + 적성 점수 */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
            <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">
              성격 특성
            </p>
            <div className="flex flex-col gap-2.5">
              {Object.entries(scores.personality_scores).map(([k, v]) => (
                <ScoreBar key={k} label={k} score={v} />
              ))}
            </div>
            {analysis.personality_description && (
              <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed border-t border-zinc-100 dark:border-zinc-800 pt-3">
                {analysis.personality_description}
              </p>
            )}
          </div>

          <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
            <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">
              적성
            </p>
            <div className="flex flex-col gap-2.5">
              {Object.entries(scores.aptitude_scores).map(([k, v]) => (
                <ScoreBar key={k} label={k} score={v} />
              ))}
            </div>
            {analysis.aptitude_description && (
              <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed border-t border-zinc-100 dark:border-zinc-800 pt-3">
                {analysis.aptitude_description}
              </p>
            )}
          </div>
        </div>

        {/* 종합 분석 */}
        <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
          <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
            종합 별자리 분석
          </p>
          <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
            {analysis.overall}
          </p>
        </div>

        {/* 실천 조언 + 행운 정보 */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
            <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">
              별자리 조언
            </p>
            <ul className="flex flex-col gap-2">
              {analysis.fortune_advice?.map((advice, i) => (
                <li
                  key={i}
                  className="flex gap-2 text-sm text-zinc-600 dark:text-zinc-400"
                >
                  <span className="text-zinc-400 dark:text-zinc-500 shrink-0">
                    {i + 1}.
                  </span>
                  {advice}
                </li>
              ))}
            </ul>
          </div>

          {analysis.lucky && (
            <div className="rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
              <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">
                행운 정보
              </p>
              <div className="flex flex-col gap-2">
                {[
                  {
                    label: "행운의 색상",
                    value: analysis.lucky.color,
                    icon: "🎨",
                  },
                  {
                    label: "행운의 방향",
                    value: analysis.lucky.direction,
                    icon: "🧭",
                  },
                  {
                    label: "행운의 숫자",
                    value: analysis.lucky.number,
                    icon: "✨",
                  },
                ].map(({ label, value, icon }) => (
                  <div
                    key={label}
                    className="flex items-center justify-between p-2 rounded-lg bg-zinc-50 dark:bg-zinc-800"
                  >
                    <span className="text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-1">
                      {icon} {label}
                    </span>
                    <span className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                      {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 액션 버튼 */}
      <div className="w-full flex flex-col gap-3 mt-6">
        <button
          onClick={handleSavePdf}
          className="w-full h-12 rounded-full border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 font-medium text-sm hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
        >
          PDF 저장
        </button>
        <button
          onClick={() => {
            sessionStorage.removeItem("zodiacResult");
            sessionStorage.removeItem("heroMatch");
            router.push("/zodiac");
          }}
          className="w-full h-12 rounded-full bg-zinc-900 text-white font-medium text-base transition-colors hover:bg-zinc-700 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
        >
          다시 분석하기
        </button>
        <button
          onClick={() => router.push("/")}
          className="text-sm text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
        >
          &larr; 메인으로
        </button>
      </div>
    </div>
  );
}
