"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import AuthGuard from "../components/AuthGuard";

import { useAuth } from "../hooks/useAuth";
import { supabase } from "../lib/supabase";

interface Profile {
  nickname: string | null;
  birth_year: number | null;
  birth_month: number | null;
  birth_day: number | null;
  birth_hour: number | null;
  gender: string | null;
  email: string;
}

interface HistoryItem {
  id: string;
  type: string;
  created_at: string;
  input_data: Record<string, unknown>;
}

const TYPE_LABELS: Record<string, string> = {
  face: "관상 분석",
  saju: "사주 분석",
  combined: "종합 분석",
};

const MyPage = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<Partial<Profile>>({});
  const [saving, setSaving] = useState(false);
  const { user, getAccessToken } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) return;
    // 프로필 로드
    supabase
      .from("profiles")
      .select("*")
      .eq("id", user.id)
      .single()
      .then(({ data }) => {
        if (data) setProfile(data);
      });
    // 이력 로드
    supabase
      .from("analysis_history")
      .select("id, type, created_at, input_data")
      .eq("user_id", user.id)
      .order("created_at", { ascending: false })
      .limit(20)
      .then(({ data }) => {
        if (data) setHistory(data);
      });
  }, [user]);

  const handleEdit = () => {
    if (!profile) return;
    setEditData({
      nickname: profile.nickname ?? "",
      birth_year: profile.birth_year,
      birth_month: profile.birth_month,
      birth_day: profile.birth_day,
      birth_hour: profile.birth_hour,
      gender: profile.gender,
    });
    setIsEditing(true);
  };

  const handleSave = useCallback(async () => {
    if (!user) return;
    setSaving(true);
    try {
      const token = await getAccessToken();
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(editData),
      });
      if (res.ok) {
        setProfile((prev) => (prev ? { ...prev, ...editData } : prev));
        setIsEditing(false);
      }
    } finally {
      setSaving(false);
    }
  }, [user, editData, getAccessToken]);

  const handleHistoryClick = (id: string) => {
    router.push(`/mypage/history/${id}`);
  };

  const inputClass =
    "w-full h-10 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-3 text-sm text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-400";

  return (
    <AuthGuard>
      <div className="flex flex-col items-center flex-1 p-4">
        <div className="w-full max-w-2xl flex flex-col gap-6">
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            마이페이지
          </h1>

          {/* 프로필 */}
          <div className="p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-zinc-900 dark:text-zinc-100">
                프로필
              </h2>
              {!isEditing ? (
                <button
                  onClick={handleEdit}
                  className="text-xs text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
                >
                  편집
                </button>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={() => setIsEditing(false)}
                    className="text-xs text-zinc-400"
                  >
                    취소
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="text-xs text-zinc-900 dark:text-zinc-100 font-medium"
                  >
                    {saving ? "저장 중..." : "저장"}
                  </button>
                </div>
              )}
            </div>

            {profile && !isEditing && (
              <div className="space-y-2 text-sm text-zinc-600 dark:text-zinc-400">
                <p>이메일: {profile.email}</p>
                <p>닉네임: {profile.nickname || "-"}</p>
                <p>
                  생년월일:{" "}
                  {profile.birth_year
                    ? `${profile.birth_year}년 ${profile.birth_month}월 ${profile.birth_day}일 ${profile.birth_hour ?? "?"}시`
                    : "미설정"}
                </p>
                <p>
                  성별:{" "}
                  {profile.gender === "male"
                    ? "남성"
                    : profile.gender === "female"
                      ? "여성"
                      : "미설정"}
                </p>
              </div>
            )}

            {isEditing && (
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">
                    닉네임
                  </label>
                  <input
                    value={editData.nickname ?? ""}
                    onChange={(e) =>
                      setEditData((d) => ({ ...d, nickname: e.target.value }))
                    }
                    className={inputClass}
                    placeholder="닉네임"
                  />
                </div>
                <div className="grid grid-cols-4 gap-2">
                  <div>
                    <label className="text-xs text-zinc-500 mb-1 block">
                      년
                    </label>
                    <input
                      type="number"
                      value={editData.birth_year ?? ""}
                      onChange={(e) =>
                        setEditData((d) => ({
                          ...d,
                          birth_year: e.target.value
                            ? parseInt(e.target.value)
                            : null,
                        }))
                      }
                      className={inputClass}
                      placeholder="1990"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-zinc-500 mb-1 block">
                      월
                    </label>
                    <input
                      type="number"
                      value={editData.birth_month ?? ""}
                      onChange={(e) =>
                        setEditData((d) => ({
                          ...d,
                          birth_month: e.target.value
                            ? parseInt(e.target.value)
                            : null,
                        }))
                      }
                      className={inputClass}
                      placeholder="1"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-zinc-500 mb-1 block">
                      일
                    </label>
                    <input
                      type="number"
                      value={editData.birth_day ?? ""}
                      onChange={(e) =>
                        setEditData((d) => ({
                          ...d,
                          birth_day: e.target.value
                            ? parseInt(e.target.value)
                            : null,
                        }))
                      }
                      className={inputClass}
                      placeholder="15"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-zinc-500 mb-1 block">
                      시
                    </label>
                    <input
                      type="number"
                      value={editData.birth_hour ?? ""}
                      onChange={(e) =>
                        setEditData((d) => ({
                          ...d,
                          birth_hour: e.target.value
                            ? parseInt(e.target.value)
                            : null,
                        }))
                      }
                      className={inputClass}
                      placeholder="14"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">
                    성별
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { value: "male", label: "남성" },
                      { value: "female", label: "여성" },
                    ].map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() =>
                          setEditData((d) => ({ ...d, gender: opt.value }))
                        }
                        className={`h-10 rounded-lg border-2 text-sm font-medium transition-all ${
                          editData.gender === opt.value
                            ? "border-zinc-900 dark:border-zinc-100 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900"
                            : "border-zinc-300 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400"
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 분석 이력 */}
          <div className="p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
              분석 이력
            </h2>
            {history.length === 0 ? (
              <p className="text-sm text-zinc-400">
                아직 분석 이력이 없습니다.
              </p>
            ) : (
              <div className="space-y-2">
                {history.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleHistoryClick(item.id)}
                    className="w-full p-3 rounded-lg border border-zinc-100 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors text-left flex items-center justify-between"
                  >
                    <div>
                      <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                        {TYPE_LABELS[item.type] ?? item.type}
                      </span>
                      <p className="text-xs text-zinc-400 mt-0.5">
                        {new Date(item.created_at).toLocaleDateString("ko-KR", {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    <svg
                      className="w-4 h-4 text-zinc-300 dark:text-zinc-600"
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
            )}
          </div>
        </div>
      </div>
    </AuthGuard>
  );
};

export default MyPage;
