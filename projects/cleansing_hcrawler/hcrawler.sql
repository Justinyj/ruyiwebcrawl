create database hcrawler;
\c hcrawler
create table hprice (
  name varchar(128),
  mainEntityOfPage varchar(32) not null,
  description varchar(1024),
  maxPrice varchar(32),
  minPrice varchar(32),
  price varchar(32),
  priceCurrency varchar(8),
  unitText varchar(16),
  priceType varchar(16),
  productionYear varchar(16),
  validDate varchar(32),
  seller varchar(512),
  productGrade varchar(32),
  productSpecification varchar(32),
  productPlaceOfOrigin varchar(32),
  sellerMarket varchar(32),
  source varchar(2048) not null,
  createdTime timestamp default now() not null,
  confidence varchar(8)
);

create tabel hmaterial (
  name varchar(128),
  description varchar(1024),
  sameAs varchar(32),
  property json,
  source varchar(2048) not null,
  createdTime timestamp default now() not null,
  confidence varchar(8)
);


