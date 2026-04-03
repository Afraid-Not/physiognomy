"use client";

import { useRouter } from "next/navigation";

const menuItems = [
  {
    title: "관상 분석",
    description: "얼굴 사진으로 AI가 관상을 분석합니다",
    href: "/face",
    icon: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z"
        />
      </svg>
    ),
  },
  {
    title: "사주 분석",
    description: "생년월일로 사주팔자를 풀어드립니다",
    href: "/saju",
    icon: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5"
        />
      </svg>
    ),
  },
  {
    title: "종합 분석",
    description: "관상 + 사주를 합쳐 종합 운세를 봅니다",
    href: "/combined",
    icon: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
        />
      </svg>
    ),
  },
];

const HomePage = () => {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <main className="w-full max-w-lg flex flex-col items-center gap-10">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">
            AI 운세
          </h1>
          <p className="mt-3 text-lg text-zinc-600 dark:text-zinc-400">
            관상과 사주로 보는 나의 운명
          </p>
        </div>

        <div className="w-full flex flex-col gap-4">
          {menuItems.map((item) => (
            <button
              key={item.href}
              onClick={() => router.push(item.href)}
              className="w-full p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-zinc-400 dark:hover:border-zinc-600 transition-all hover:shadow-md text-left flex items-center gap-4 group"
            >
              <div className="shrink-0 w-14 h-14 rounded-xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-500 dark:text-zinc-400 group-hover:text-zinc-900 dark:group-hover:text-zinc-100 transition-colors">
                {item.icon}
              </div>
              <div>
                <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                  {item.title}
                </h2>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">
                  {item.description}
                </p>
              </div>
              <svg
                className="w-5 h-5 ml-auto shrink-0 text-zinc-300 dark:text-zinc-600 group-hover:text-zinc-500 dark:group-hover:text-zinc-400 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          ))}
        </div>

        <p className="text-xs text-zinc-300 dark:text-zinc-600 text-center">
          본 서비스는 전통 관상학/명리학에 기반한 재미 목적의 분석이며, 과학적
          근거가 아닙니다.
        </p>
      </main>
    </div>
  );
};

export default HomePage;
