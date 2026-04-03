-- ============================================
-- 1. profiles 테이블 (auth.users 확장)
-- ============================================
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  nickname text,
  birth_year int,
  birth_month int,
  birth_day int,
  birth_hour int,
  gender text check (gender in ('male', 'female')),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- RLS 활성화
alter table public.profiles enable row level security;

-- 본인만 읽기/수정
create policy "profiles_select_own" on public.profiles
  for select using (auth.uid() = id);

create policy "profiles_update_own" on public.profiles
  for update using (auth.uid() = id);

create policy "profiles_insert_own" on public.profiles
  for insert with check (auth.uid() = id);

-- 회원가입 시 자동으로 profiles 행 생성
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email);
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();


-- ============================================
-- 2. analysis_history 테이블
-- ============================================
create table if not exists public.analysis_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  type text not null check (type in ('face', 'saju', 'combined')),
  input_data jsonb not null default '{}',
  result_data jsonb not null default '{}',
  image_url text,
  created_at timestamptz default now()
);

-- 인덱스
create index if not exists idx_history_user_id on public.analysis_history(user_id);
create index if not exists idx_history_created_at on public.analysis_history(created_at desc);

-- RLS 활성화
alter table public.analysis_history enable row level security;

-- 본인 이력만 읽기/쓰기
create policy "history_select_own" on public.analysis_history
  for select using (auth.uid() = user_id);

create policy "history_insert_own" on public.analysis_history
  for insert with check (auth.uid() = user_id);


-- ============================================
-- 3. Storage 버킷 (업로드 사진 저장)
-- ============================================
insert into storage.buckets (id, name, public)
values ('face-images', 'face-images', false)
on conflict (id) do nothing;

-- 본인 폴더에만 업로드/읽기
create policy "face_images_insert" on storage.objects
  for insert with check (
    bucket_id = 'face-images'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy "face_images_select" on storage.objects
  for select using (
    bucket_id = 'face-images'
    and (storage.foldername(name))[1] = auth.uid()::text
  );
