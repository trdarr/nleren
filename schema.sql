create extension pgcrypto;

create table words (
  word_id uuid primary key default gen_random_uuid(),
  word text not null,
  pos text not null,
  "order" smallint not null unique,
  cefr smallint not null check (cefr >= 1 and cefr <= 6),
  example text,
  grammar text
);

create index words_cefr_idx on words (cefr);
create index words_order_idx on words ("order");

create table translations (
  translation_id uuid primary key default gen_random_uuid(),
  word_id uuid not null references words on delete cascade,
  translation text not null,
  source text not null
);
