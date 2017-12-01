drop table if exists entries;
create table entries(
    id integer primary key AUTOINCREMENT,
    long string not null,
    short string
);