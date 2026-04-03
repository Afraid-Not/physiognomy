"use client";

const TermsPage = () => {
  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-6">
        이용약관
      </h1>

      <div className="space-y-6 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제1조 (목적)
          </h2>
          <p>
            본 약관은 점.ZIP(이하 &quot;서비스&quot;)의 이용 조건 및 절차에 관한
            기본 사항을 규정합니다.
          </p>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제2조 (서비스의 내용)
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>AI 기반 관상 분석</li>
            <li>사주팔자 분석</li>
            <li>관상 + 사주 종합 분석</li>
            <li>분석 이력 저장 및 조회</li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제3조 (서비스의 성격)
          </h2>
          <p>
            본 서비스는 <strong>오락 및 엔터테인먼트 목적</strong>으로
            제공됩니다. 분석 결과는 과학적 근거가 없으며, 의료, 법률, 재정 등
            중요한 의사결정의 근거로 사용해서는 안 됩니다. 서비스 제공자는 분석
            결과에 기반한 이용자의 판단이나 행동에 대해 책임을 지지 않습니다.
          </p>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제4조 (이용자의 의무)
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>타인의 사진을 무단으로 사용하여 분석하지 않습니다.</li>
            <li>서비스를 악용하거나 비정상적인 방법으로 이용하지 않습니다.</li>
            <li>
              분석 결과를 타인에게 불이익을 주는 용도로 사용하지 않습니다.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제5조 (서비스 이용료)
          </h2>
          <p>본 서비스는 무료로 제공됩니다.</p>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제6조 (면책 조항)
          </h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              서비스 제공자는 분석 결과의 정확성이나 신뢰성을 보장하지 않습니다.
            </li>
            <li>
              천재지변, 시스템 장애 등 불가항력으로 인한 서비스 중단에 대해
              책임을 지지 않습니다.
            </li>
            <li>
              이용자가 서비스를 통해 얻은 정보에 의한 손해에 대해 책임을 지지
              않습니다.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제7조 (약관의 변경)
          </h2>
          <p>
            본 약관은 서비스 내 공지를 통해 변경될 수 있으며, 변경된 약관은 공지
            즉시 효력이 발생합니다.
          </p>
        </section>

        <section>
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            제8조 (시행일)
          </h2>
          <p>본 약관은 2026년 4월 4일부터 시행됩니다.</p>
        </section>
      </div>
    </div>
  );
};

export default TermsPage;
