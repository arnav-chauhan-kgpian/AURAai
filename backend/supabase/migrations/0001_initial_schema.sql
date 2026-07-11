-- AuraAI — initial production schema
-- Tables: users, profiles, sessions, conversations, skin_scans, try_on_jobs,
--         recommendations, audit_logs
--
-- Conventions:
--   * All ids are text (Clerk user ids are strings; server-generated ids are hex).
--   * Every row has created_at/updated_at; user data has deleted_at (soft delete).
--   * RLS is enabled with a default-deny posture. The backend uses the Supabase
--     service_role key, which bypasses RLS; the anon/authenticated roles get no
--     access unless an explicit policy is added (see the commented Clerk example).

create extension if not exists "pgcrypto";

-- updated_at maintenance ------------------------------------------------------
create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- users -----------------------------------------------------------------------
create table if not exists users (
  id          text primary key,               -- Clerk user id (sub)
  org_id      text not null,
  email       text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  deleted_at  timestamptz
);
create index if not exists idx_users_org on users (org_id);

-- profiles --------------------------------------------------------------------
create table if not exists profiles (
  user_id          text primary key references users (id) on delete cascade,
  org_id           text not null,
  skin_type        text,
  fitzpatrick_type text,
  undertone        text,
  preferred_style  text,
  favorite_colors  jsonb not null default '[]'::jsonb,
  consent_granted  boolean not null default false,
  consent_at       timestamptz,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  deleted_at       timestamptz
);

-- sessions --------------------------------------------------------------------
create table if not exists sessions (
  id                text primary key,
  user_id           text not null references users (id) on delete cascade,
  org_id            text not null,
  clerk_session_id  text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  deleted_at        timestamptz
);
create index if not exists idx_sessions_user on sessions (user_id);
create index if not exists idx_sessions_org on sessions (org_id);

-- conversations ---------------------------------------------------------------
create table if not exists conversations (
  id          text primary key,
  session_id  text not null references sessions (id) on delete cascade,
  user_id     text not null references users (id) on delete cascade,
  org_id      text not null,
  role        text not null check (role in ('user', 'assistant', 'system')),
  content     text not null,
  created_at  timestamptz not null default now(),
  deleted_at  timestamptz
);
create index if not exists idx_conversations_session on conversations (session_id, created_at);
create index if not exists idx_conversations_user on conversations (user_id);

-- skin_scans (metadata only — never raw biometric pixels) ---------------------
create table if not exists skin_scans (
  id          text primary key,
  user_id     text not null references users (id) on delete cascade,
  org_id      text not null,
  session_id  text references sessions (id) on delete set null,
  image_key   text,                            -- Supabase Storage object key
  task_id     text,
  scores      jsonb not null default '[]'::jsonb,
  overlays    jsonb not null default '[]'::jsonb,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  deleted_at  timestamptz
);
create index if not exists idx_skin_scans_user on skin_scans (user_id);
create index if not exists idx_skin_scans_session on skin_scans (session_id);

-- try_on_jobs -----------------------------------------------------------------
create table if not exists try_on_jobs (
  id                text primary key,
  user_id           text not null references users (id) on delete cascade,
  org_id            text not null,
  session_id        text references sessions (id) on delete set null,
  person_image_key  text,
  garment_image_key text,
  task_id           text,
  status            text not null default 'pending',
  output_images     jsonb not null default '[]'::jsonb,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  deleted_at        timestamptz
);
create index if not exists idx_try_on_user on try_on_jobs (user_id);
create index if not exists idx_try_on_session on try_on_jobs (session_id);

-- recommendations -------------------------------------------------------------
create table if not exists recommendations (
  id          text primary key,
  user_id     text not null references users (id) on delete cascade,
  org_id      text not null,
  session_id  text references sessions (id) on delete set null,
  payload     jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now(),
  deleted_at  timestamptz
);
create index if not exists idx_recommendations_user on recommendations (user_id);
create index if not exists idx_recommendations_session on recommendations (session_id);

-- audit_logs (append-only) ----------------------------------------------------
create table if not exists audit_logs (
  id              text primary key,
  user_id         text,
  org_id          text,
  session_id      text,
  action          text not null,
  resource        text,
  correlation_id  text,
  ip_address      text,
  metadata        jsonb not null default '{}'::jsonb,
  created_at      timestamptz not null default now()
);
create index if not exists idx_audit_user on audit_logs (user_id, created_at);
create index if not exists idx_audit_action on audit_logs (action, created_at);

-- updated_at triggers ---------------------------------------------------------
create trigger trg_users_updated     before update on users      for each row execute function set_updated_at();
create trigger trg_profiles_updated  before update on profiles   for each row execute function set_updated_at();
create trigger trg_sessions_updated  before update on sessions   for each row execute function set_updated_at();
create trigger trg_skin_updated      before update on skin_scans for each row execute function set_updated_at();
create trigger trg_tryon_updated     before update on try_on_jobs for each row execute function set_updated_at();

-- Row Level Security: default-deny. The backend uses service_role (bypasses
-- RLS). anon/authenticated roles get nothing unless a policy is added.
alter table users            enable row level security;
alter table profiles         enable row level security;
alter table sessions         enable row level security;
alter table conversations    enable row level security;
alter table skin_scans       enable row level security;
alter table try_on_jobs      enable row level security;
alter table recommendations  enable row level security;
alter table audit_logs       enable row level security;

-- Example (commented): if you wire Clerk as a Supabase third-party JWT provider,
-- scope access to the caller's own rows. Until then, default-deny stands.
--
-- create policy "own rows" on profiles for select to authenticated
--   using (user_id = (auth.jwt() ->> 'sub'));
