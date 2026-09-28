create table if not exists predictions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  as_of_date date not null,
  ticker text not null,
  current_price numeric not null,
  predicted_price numeric not null,
  predicted_return numeric not null,
  weight numeric not null
);

create index if not exists predictions_as_of_date_idx
  on predictions (as_of_date desc);

alter table predictions enable row level security;

create policy "Public read access"
  on predictions for select
  using (true);
