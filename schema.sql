-- Apply once to a dedicated Supabase project after inspecting existing tables.
begin;
create table public.content_items (
  id uuid primary key default gen_random_uuid(),
  title text not null check (length(trim(title)) > 0),
  platform text,
  status text not null default 'idea'
    check (status in ('idea','draft','production','ready','published','archived')),
  due_date date,
  published_url text,
  notes text,
  created_at timestamptz not null default now()
);
create table public.daily_reviews (
  review_date date not null,
  timezone text not null,
  total_items integer not null check (total_items >= 0),
  status_counts jsonb not null,
  due_items integer not null check (due_items >= 0),
  primary key (review_date, timezone)
);
alter table public.content_items enable row level security;
alter table public.daily_reviews enable row level security;
revoke all on public.content_items, public.daily_reviews from anon, authenticated;
grant select, insert, update, delete on public.content_items to service_role;
grant select, insert, update on public.daily_reviews to service_role;
commit;
