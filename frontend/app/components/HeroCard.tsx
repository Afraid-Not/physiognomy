"use client";

interface HeroData {
  name: string;
  title: string;
  description: string;
  tags: string[];
  match_score: number;
  common_traits: string[];
}

const HeroCard = ({ hero }: { hero: HeroData }) => {
  return (
    <div className="w-full p-5 rounded-2xl border-2 border-amber-200 dark:border-amber-800 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30">
      <div className="flex items-start gap-4">
        {/* 위인 아이콘 placeholder (나중에 이미지로 교체) */}
        <div className="shrink-0 w-16 h-16 rounded-full bg-amber-100 dark:bg-amber-900 flex items-center justify-center text-2xl border-2 border-amber-300 dark:border-amber-700">
          <span className="text-amber-700 dark:text-amber-300 font-bold">
            {hero.name[0]}
          </span>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
              {hero.name}
            </h3>
            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-200 dark:bg-amber-800 text-amber-800 dark:text-amber-200 font-medium">
              {hero.match_score}% 일치
            </span>
          </div>
          <p className="text-sm font-medium text-amber-700 dark:text-amber-400 mt-0.5">
            {hero.title}
          </p>
          <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-2 leading-relaxed">
            {hero.description}
          </p>

          {/* 공통 특성 */}
          {hero.common_traits.length > 0 && (
            <div className="flex items-center gap-1.5 mt-2 flex-wrap">
              <span className="text-[10px] text-zinc-400">공통 특성:</span>
              {hero.common_traits.map((trait) => (
                <span
                  key={trait}
                  className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300"
                >
                  {trait}
                </span>
              ))}
            </div>
          )}

          {/* 태그 */}
          <div className="flex gap-1.5 mt-2 flex-wrap">
            {hero.tags.map((tag) => (
              <span
                key={tag}
                className="text-[10px] px-1.5 py-0.5 rounded border border-zinc-200 dark:border-zinc-700 text-zinc-500 dark:text-zinc-400"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroCard;
