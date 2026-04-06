-- analysis_history.type 체크 제약조건에 'tarot' 추가
ALTER TABLE public.analysis_history
  DROP CONSTRAINT analysis_history_type_check;

ALTER TABLE public.analysis_history
  ADD CONSTRAINT analysis_history_type_check
  CHECK (type IN ('face', 'saju', 'combined', 'tarot'));
