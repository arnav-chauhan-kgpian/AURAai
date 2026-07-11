# Migrations

SQL migrations live in [`backend/supabase/migrations/`](backend/supabase/migrations/)
and are designed for Supabase (Postgres).

| File | Purpose |
| --- | --- |
| `0001_initial_schema.sql` | All 8 tables, triggers, indexes, FKs, RLS (default-deny) |
| `0002_storage.sql` | Creates the private `aura-uploads` Storage bucket |

Migrations are **idempotent** (`create table if not exists`, `on conflict do
nothing`), so re-running is safe.

## Apply with the Supabase CLI (recommended)

```bash
# One-time
npm i -g supabase
supabase login
supabase link --project-ref <your-project-ref>

# Apply everything in order
supabase db push
```

## Apply via the SQL editor

Open the Supabase dashboard → SQL Editor and run the files **in numeric order**
(`0001` then `0002`). Paste the file contents and execute.

## Apply with psql

```bash
psql "$SUPABASE_DB_URL" -f backend/supabase/migrations/0001_initial_schema.sql
psql "$SUPABASE_DB_URL" -f backend/supabase/migrations/0002_storage.sql
```

## Verify

```sql
select table_name from information_schema.tables
where table_schema = 'public'
  and table_name in ('users','profiles','sessions','conversations',
                     'skin_scans','try_on_jobs','recommendations','audit_logs');
-- expect 8 rows

select id from storage.buckets where id = 'aura-uploads';  -- expect 1 row
```

## Adding a migration

Create the next numbered file (`0003_*.sql`). Keep changes additive and
idempotent; never edit a released migration — add a new one.

## Rollback

These migrations don't ship destructive `down` scripts (data-loss risk on a live
DB). To reverse in a non-production environment, drop the created objects
manually, or restore from a Supabase backup / point-in-time recovery.

## RLS note

RLS is enabled with **no permissive policies** — access is via the service-role
key only. To expose rows to authenticated clients directly (e.g., wiring Clerk as
a Supabase third-party JWT), add per-row policies; a commented example scoping
`profiles` to `auth.jwt() ->> 'sub'` is in `0001_initial_schema.sql`.
