create database crawlercache;
\c crawlercache;

create table accessed (
  id bigserial primary key,
  batch_id varchar(64),
  workgroup varchar(64),
  status smallint, -- 0 begin, 1 downloaded
  url varchar(2048),
  url_hash varchar(128),
  created_time timestamp default now(),
  updated_time timestamp
);
create index accessed_url_idx on accessed (url);
create unique index accessed_batchid_urlhash_idx on accessed (batch_id, url_hash);


create table cached (
  id bigserial primary key,
  url varchar(2048),
  created_time timestamp default now(),
  last_modify timestamp,
  url_hash varchar(128),
  content_hash varchar(256)
);
create index cached_url_idx on cached (url);
create index cached_url_hash_idx on cached (url_hash);


create table contents (
  id bigserial primary key,
  cached_id bigint references cached (id) not null,
  content text
);
create index contents_cached_id_idx on contents (cached_id);
