import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";
import NavBar from "./components/NavBar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "점zip | AI로 운세 체크",
  description: "AI로 운세 체크 - 관상, 사주, 타로로 보는 나의 운명",
  icons: { icon: "/favicon.svg" },
};

const RootLayout = ({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) => {
  return (
    <html
      lang="ko"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-zinc-100 dark:bg-zinc-950 p-4">
        <div className="mx-auto flex flex-col lg:flex-row items-start justify-center gap-2 min-h-[calc(100vh-2rem)] lg:w-fit">
          {/* 왼쪽 배너 - 데스크탑 */}
          <aside className="hidden lg:flex w-[160px] shrink-0 sticky top-4 h-[600px] rounded-2xl border border-dashed border-zinc-300 dark:border-zinc-700 bg-white/50 dark:bg-zinc-900/50 items-center justify-center">
            <span className="text-xs text-zinc-400 dark:text-zinc-600">AD</span>
          </aside>

          {/* 메인 앱 */}
          <div className="w-[448px] lg:w-[560px] max-w-full shrink-0 h-[calc(100vh-2rem)] bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-lg overflow-y-auto flex flex-col">
            <NavBar />
            {children}
          </div>

          {/* 오른쪽 배너 - 데스크탑 */}
          <aside className="hidden lg:flex w-[160px] shrink-0 sticky top-4 h-[600px] rounded-2xl border border-dashed border-zinc-300 dark:border-zinc-700 bg-white/50 dark:bg-zinc-900/50 items-center justify-center">
            <span className="text-xs text-zinc-400 dark:text-zinc-600">AD</span>
          </aside>

          {/* 하단 배너 - 모바일 */}
          <div className="flex lg:hidden w-full max-w-md mx-auto gap-3">
            <div className="flex-1 h-[100px] rounded-xl border border-dashed border-zinc-300 dark:border-zinc-700 bg-white/50 dark:bg-zinc-900/50 flex items-center justify-center">
              <span className="text-xs text-zinc-400 dark:text-zinc-600">
                AD
              </span>
            </div>
            <div className="flex-1 h-[100px] rounded-xl border border-dashed border-zinc-300 dark:border-zinc-700 bg-white/50 dark:bg-zinc-900/50 flex items-center justify-center">
              <span className="text-xs text-zinc-400 dark:text-zinc-600">
                AD
              </span>
            </div>
          </div>
        </div>
        <Analytics />
      </body>
    </html>
  );
};

export default RootLayout;
