"use client";

const PrivacyPage = () => {
  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
        개인정보처리방침
      </h1>

      <div className="space-y-6 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            1. 수집하는 개인정보 항목
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>회원가입 시: 이메일 주소, 비밀번호</li>
            <li>분석 이용 시: 생년월일, 성별, 출생 시간</li>
            <li>
              얼굴 사진: 로그인 사용자의 경우 분석 이력 보관을 위해 Supabase
              Storage에 저장됩니다. 비회원의 경우 분석 처리 후 즉시 폐기됩니다.
            </li>
            <li>
              비회원 분석 이용 시: 서비스 이용 통계 목적으로{" "}
              <strong>IP 주소</strong>와 분석 유형(관상/사주/타로/종합), 이용
              시각이 수집됩니다.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            2. 개인정보의 수집 및 이용 목적
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>관상, 사주, 종합 분석 서비스 제공</li>
            <li>분석 이력 저장 및 조회</li>
            <li>회원 식별 및 인증</li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            3. 개인정보의 보유 및 이용 기간
          </h2>
          <p>
            회원 탈퇴 시까지 보유하며, 탈퇴 즉시 모든 개인정보와 분석 이력을
            삭제합니다.
          </p>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            4. 개인정보의 제3자 제공
          </h2>
          <p>
            수집된 개인정보는 제3자에게 제공하지 않습니다. 다만, 서비스 운영을
            위해 다음의 외부 서비스를 이용합니다:
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-1">
            <li>Supabase: 회원 인증 및 데이터 저장</li>
            <li>OpenAI API: AI 분석 처리</li>
            <li>Vercel Analytics: 방문자 통계 (비식별 정보)</li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            5. 이용자의 권리
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              언제든지 회원 탈퇴를 통해 개인정보 삭제를 요청할 수 있습니다.
            </li>
            <li>마이페이지에서 개인정보를 열람 및 수정할 수 있습니다.</li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            6. 개인정보의 안전성 확보 조치
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>비밀번호는 암호화되어 저장됩니다.</li>
            <li>HTTPS를 통한 데이터 전송 암호화를 적용합니다.</li>
            <li>데이터베이스 접근은 행 수준 보안(RLS) 정책으로 보호됩니다.</li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            7. 시행일
          </h2>
          <p>본 개인정보처리방침은 2026년 4월 4일부터 시행됩니다.</p>
        </section>
      </div>
    </div>
  );
};

export default PrivacyPage;
