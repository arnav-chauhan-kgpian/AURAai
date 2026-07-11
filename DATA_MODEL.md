# Data Model

Defined in [`backend/supabase/migrations/0001_initial_schema.sql`](backend/supabase/migrations/0001_initial_schema.sql).

## Conventions

- **Ids** are `text`. Clerk user ids are strings; server-generated ids are hex
  (`app/db/repositories.py::new_id`). Clients never generate persisted ids.
- **Timestamps**: every table has `created_at`; mutable tables have `updated_at`
  (maintained by a trigger).
- **Soft delete**: user-scoped tables carry `deleted_at`; deletes set it rather
  than removing rows. Reads filter `deleted_at is null`.
- **RLS**: enabled on every table, default-deny. The backend uses the service-role
  key (bypasses RLS); anon/authenticated roles get nothing.

## Tables

### `users`
The account. `id` = Clerk user id. Columns: `org_id`, `email`, timestamps, `deleted_at`.

### `profiles` (1:1 with users)
Durable preferences + consent. `user_id` PK → `users(id)`. Columns: `skin_type`,
`fitzpatrick_type`, `undertone`, `preferred_style`, `favorite_colors` (jsonb),
`consent_granted` (bool), `consent_at`.

### `sessions`
A conversation session, **server-owned**. `id` PK, `user_id` → users, `org_id`,
`clerk_session_id`. Ownership of a session is validated on every request.

### `conversations`
Message history. `id` PK, `session_id` → sessions, `user_id` → users, `role`
(`user`/`assistant`/`system`), `content`. Indexed by `(session_id, created_at)`.

### `skin_scans`
Skin-analysis records — **metadata only, never raw pixels**. `id` PK, `user_id`,
`session_id`, `image_key` (Storage object key), `task_id`, `scores` (jsonb),
`overlays` (jsonb).

### `try_on_jobs`
Virtual try-on jobs. `id` PK, `user_id`, `session_id`, `person_image_key`,
`garment_image_key`, `task_id`, `status`, `output_images` (jsonb).

### `recommendations`
Generated recommendation sets. `id` PK, `user_id`, `session_id`, `payload` (jsonb).

### `audit_logs` (append-only)
`id` PK, `user_id`, `org_id`, `session_id`, `action`, `resource`, `correlation_id`,
`ip_address`, `metadata` (jsonb), `created_at`. Written for chat runs, consent
changes, and deletions.

## Relationships

```
users 1───1 profiles
  │
  1───* sessions ───* conversations
  │            └────* skin_scans
  │            └────* try_on_jobs
  │            └────* recommendations
  └───* audit_logs
```

Child rows reference `users(id)` / `sessions(id)` with `ON DELETE CASCADE` (a hard
user delete cleans up), though normal deletion is soft (`deleted_at`).

## Storage

User images live in the private `aura-uploads` Supabase Storage bucket, keyed
`<user_id>/<id>`, served only via short-lived signed URLs and swept after
`IMAGE_RETENTION_DAYS`.
