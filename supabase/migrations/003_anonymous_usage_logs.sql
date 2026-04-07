-- 비회원 사용 로그 테이블
CREATE TABLE anonymous_usage_logs (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    analysis_type text NOT NULL CHECK (analysis_type IN ('face', 'saju', 'tarot', 'combined')),
    category text,           -- 타로 카테고리 (타로/종합일 때만)
    ip_address text,
    created_at timestamptz DEFAULT now() NOT NULL
);

-- 조회 성능용 인덱스
CREATE INDEX idx_anonymous_usage_logs_created_at ON anonymous_usage_logs (created_at DESC);
CREATE INDEX idx_anonymous_usage_logs_analysis_type ON anonymous_usage_logs (analysis_type);
