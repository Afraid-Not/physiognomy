-- anonymous_usage_logs에 zodiac 분석 타입 추가
ALTER TABLE anonymous_usage_logs
    DROP CONSTRAINT anonymous_usage_logs_analysis_type_check;

ALTER TABLE anonymous_usage_logs
    ADD CONSTRAINT anonymous_usage_logs_analysis_type_check
    CHECK (analysis_type IN ('face', 'saju', 'tarot', 'combined', 'zodiac'));
