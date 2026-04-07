"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../hooks/useAuth";

// ─────────────────────────────────────────────
// 도시 목록 (lat, lng, timezone)
// ─────────────────────────────────────────────
const CITIES = [
  // 한국
  { group: "한국", name: "서울", lat: 37.5665, lng: 126.978, tz: "Asia/Seoul" },
  {
    group: "한국",
    name: "부산",
    lat: 35.1796,
    lng: 129.0756,
    tz: "Asia/Seoul",
  },
  {
    group: "한국",
    name: "대구",
    lat: 35.8714,
    lng: 128.6014,
    tz: "Asia/Seoul",
  },
  {
    group: "한국",
    name: "인천",
    lat: 37.4563,
    lng: 126.7052,
    tz: "Asia/Seoul",
  },
  {
    group: "한국",
    name: "광주",
    lat: 35.1595,
    lng: 126.8526,
    tz: "Asia/Seoul",
  },
  {
    group: "한국",
    name: "대전",
    lat: 36.3504,
    lng: 127.3845,
    tz: "Asia/Seoul",
  },
  {
    group: "한국",
    name: "울산",
    lat: 35.5384,
    lng: 129.3114,
    tz: "Asia/Seoul",
  },
  {
    group: "한국",
    name: "수원",
    lat: 37.2636,
    lng: 127.0286,
    tz: "Asia/Seoul",
  },
  {
    group: "한국",
    name: "제주",
    lat: 33.4996,
    lng: 126.5312,
    tz: "Asia/Seoul",
  },
  // 아시아
  {
    group: "아시아",
    name: "도쿄 (일본)",
    lat: 35.6762,
    lng: 139.6503,
    tz: "Asia/Tokyo",
  },
  {
    group: "아시아",
    name: "오사카 (일본)",
    lat: 34.6937,
    lng: 135.5023,
    tz: "Asia/Tokyo",
  },
  {
    group: "아시아",
    name: "베이징 (중국)",
    lat: 39.9042,
    lng: 116.4074,
    tz: "Asia/Shanghai",
  },
  {
    group: "아시아",
    name: "상하이 (중국)",
    lat: 31.2304,
    lng: 121.4737,
    tz: "Asia/Shanghai",
  },
  {
    group: "아시아",
    name: "홍콩",
    lat: 22.3193,
    lng: 114.1694,
    tz: "Asia/Hong_Kong",
  },
  {
    group: "아시아",
    name: "싱가포르",
    lat: 1.3521,
    lng: 103.8198,
    tz: "Asia/Singapore",
  },
  {
    group: "아시아",
    name: "방콕 (태국)",
    lat: 13.7563,
    lng: 100.5018,
    tz: "Asia/Bangkok",
  },
  {
    group: "아시아",
    name: "뭄바이 (인도)",
    lat: 19.076,
    lng: 72.8777,
    tz: "Asia/Kolkata",
  },
  {
    group: "아시아",
    name: "두바이 (UAE)",
    lat: 25.2048,
    lng: 55.2708,
    tz: "Asia/Dubai",
  },
  // 유럽
  {
    group: "유럽",
    name: "런던 (영국)",
    lat: 51.5074,
    lng: -0.1278,
    tz: "Europe/London",
  },
  {
    group: "유럽",
    name: "파리 (프랑스)",
    lat: 48.8566,
    lng: 2.3522,
    tz: "Europe/Paris",
  },
  {
    group: "유럽",
    name: "베를린 (독일)",
    lat: 52.52,
    lng: 13.405,
    tz: "Europe/Berlin",
  },
  {
    group: "유럽",
    name: "로마 (이탈리아)",
    lat: 41.9028,
    lng: 12.4964,
    tz: "Europe/Rome",
  },
  {
    group: "유럽",
    name: "마드리드 (스페인)",
    lat: 40.4168,
    lng: -3.7038,
    tz: "Europe/Madrid",
  },
  // 아메리카
  {
    group: "아메리카",
    name: "뉴욕 (미국)",
    lat: 40.7128,
    lng: -74.006,
    tz: "America/New_York",
  },
  {
    group: "아메리카",
    name: "로스앤젤레스 (미국)",
    lat: 34.0522,
    lng: -118.2437,
    tz: "America/Los_Angeles",
  },
  {
    group: "아메리카",
    name: "시카고 (미국)",
    lat: 41.8781,
    lng: -87.6298,
    tz: "America/Chicago",
  },
  {
    group: "아메리카",
    name: "밴쿠버 (캐나다)",
    lat: 49.2827,
    lng: -123.1207,
    tz: "America/Vancouver",
  },
  {
    group: "아메리카",
    name: "상파울루 (브라질)",
    lat: -23.5505,
    lng: -46.6333,
    tz: "America/Sao_Paulo",
  },
  // 오세아니아
  {
    group: "오세아니아",
    name: "시드니 (호주)",
    lat: -33.8688,
    lng: 151.2093,
    tz: "Australia/Sydney",
  },
  {
    group: "오세아니아",
    name: "멜버른 (호주)",
    lat: -37.8136,
    lng: 144.9631,
    tz: "Australia/Melbourne",
  },
];

// ─────────────────────────────────────────────
// '?' 툴팁 컴포넌트
// ─────────────────────────────────────────────
const TooltipIcon = ({ content }: { content: string }) => {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="ml-1 w-4 h-4 rounded-full bg-zinc-200 dark:bg-zinc-700 text-zinc-500 dark:text-zinc-400 text-xs font-bold inline-flex items-center justify-center hover:bg-zinc-300 dark:hover:bg-zinc-600 transition-colors"
        aria-label="도움말"
      >
        ?
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute z-20 left-0 mt-1 w-64 p-3 rounded-xl bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 shadow-lg text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed">
            {content}
          </div>
        </>
      )}
    </span>
  );
};

const HOURS = Array.from({ length: 24 }, (_, i) => i);

const ZodiacPage = () => {
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [hour, setHour] = useState("");
  const [minute, setMinute] = useState("0");
  const [cityKey, setCityKey] = useState("서울");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { getAccessToken } = useAuth();

  const selectedCity = CITIES.find((c) => c.name === cityKey) ?? CITIES[0];

  const handleSubmit = useCallback(async () => {
    if (!year || !month || !day || hour === "") {
      setError("생년월일과 출생 시간을 모두 입력해주세요.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setLoadingStep("별자리를 계산하고 있어요...");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const token = await getAccessToken();

      const body = {
        birth_year: Number(year),
        birth_month: Number(month),
        birth_day: Number(day),
        birth_hour: Number(hour),
        birth_minute: Number(minute),
        latitude: selectedCity.lat,
        longitude: selectedCity.lng,
        timezone: selectedCity.tz,
        stream: true,
      };

      const res = await fetch(`${apiUrl}/api/zodiac`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(body),
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
          const jsonStr = line.slice(6);
          try {
            const msg = JSON.parse(jsonStr);

            if (msg.type === "classified") {
              classifiedData = msg.data;
              if (msg.hero)
                sessionStorage.setItem("heroMatch", JSON.stringify(msg.hero));
              setLoadingStep("별자리 해석을 작성하고 있어요...");
            } else if (msg.type === "chunk") {
              setLoadingStep("별자리 분석을 작성하고 있어요...");
            } else if (msg.type === "done") {
              sessionStorage.setItem(
                "zodiacResult",
                JSON.stringify({
                  classified: classifiedData,
                  analysis: msg.data,
                }),
              );
              router.push("/zodiac/result");
              return;
            } else if (msg.type === "error") {
              throw new Error(msg.data);
            }
          } catch {
            // incomplete chunk
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
  }, [year, month, day, hour, minute, selectedCity, router, getAccessToken]);

  const inputClass =
    "w-full h-12 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-400 dark:focus:ring-zinc-500 transition-shadow";

  const groups = [...new Set(CITIES.map((c) => c.group))];

  return (
    <div className="flex flex-col items-center justify-center flex-1 p-6">
      <main className="w-full flex flex-col items-center gap-6">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">
            별자리 분석
          </h1>
          <p className="mt-3 text-lg text-zinc-600 dark:text-zinc-400">
            태양궁 · 달궁 · 상승궁으로 성격과 적성을 분석합니다
          </p>
        </div>

        {/* 별자리 3궁 안내 */}
        <div className="w-full rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 p-4 flex flex-col gap-3">
          <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">
            3궁이란?
          </p>
          <div className="flex flex-col gap-2">
            {[
              {
                symbol: "☀️",
                label: "태양궁 (Sun Sign)",
                desc: "생년월일로 계산. 핵심 자아와 의식적 정체성을 나타냅니다. 우리가 흔히 '나는 OO자리'라고 부르는 별자리입니다.",
              },
              {
                symbol: "🌙",
                label: "달궁 (Moon Sign)",
                desc: "생년월일 + 출생 시간으로 계산. 내면의 감정 세계, 본능적 반응, 무의식적 욕구를 나타냅니다. 친한 사람들에게만 보이는 진짜 나의 모습입니다.",
              },
              {
                symbol: "⬆️",
                label: "상승궁 (Rising Sign)",
                desc: "생년월일 + 출생 시간 + 장소로 계산. 타인에게 보이는 첫인상과 사회적 이미지를 나타냅니다. 가장 정밀한 계산이 필요합니다.",
              },
            ].map((item) => (
              <div key={item.label} className="flex gap-3 items-start">
                <span className="text-lg mt-0.5">{item.symbol}</span>
                <div>
                  <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    {item.label}
                  </p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 생년월일 */}
        <div className="w-full flex flex-col gap-4">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
                년
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

          {/* 출생 시간 */}
          <div>
            <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
              출생 시간
              <TooltipIcon content="달궁과 상승궁 계산에 필요합니다. 출생 시간을 모르면 정오(12시)를 입력하면 태양궁만이라도 정확하게 계산됩니다." />
            </label>
            <div className="grid grid-cols-2 gap-3">
              <select
                value={hour}
                onChange={(e) => setHour(e.target.value)}
                className={inputClass}
              >
                <option value="">시 선택</option>
                {HOURS.map((h) => (
                  <option key={h} value={h}>
                    {String(h).padStart(2, "0")}시
                  </option>
                ))}
              </select>
              <select
                value={minute}
                onChange={(e) => setMinute(e.target.value)}
                className={inputClass}
              >
                {[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55].map((m) => (
                  <option key={m} value={m}>
                    {String(m).padStart(2, "0")}분
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 출생 도시 */}
          <div>
            <label className="text-xs text-zinc-500 dark:text-zinc-400 mb-1 block">
              출생 도시
              <TooltipIcon content="상승궁(Rising Sign) 계산에는 출생 장소의 위도와 경도가 필요합니다. 실제 출생지에 가장 가까운 도시를 선택해주세요." />
            </label>
            <select
              value={cityKey}
              onChange={(e) => setCityKey(e.target.value)}
              className={inputClass}
            >
              {groups.map((group) => (
                <optgroup key={group} label={group}>
                  {CITIES.filter((c) => c.group === group).map((city) => (
                    <option key={city.name} value={city.name}>
                      {city.name}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
            <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
              위도 {selectedCity.lat.toFixed(2)}° / 경도{" "}
              {selectedCity.lng.toFixed(2)}°
            </p>
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
            "별자리 분석하기"
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

export default ZodiacPage;
