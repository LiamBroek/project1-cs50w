CREATE TABLE users(
	user_id serial primary key,
	username VARCHAR NOT NULL,
	fname VARCHAR NOT NULL,
	sname VARCHAR NOT NULL,
	password VARCHAR NOT NULL,
	email VARCHAR
	);


CREATE TABLE reviews(
	review_id serial primary key,
	user_id integer NOT NULL,
	book_id integer NOT NULL,
	review varchar NOT NULL,
	rating varchar
	);


CREATE TABLE books(
	book_id serial primary key,
	isbn varchar NOT NULL,
	title varchar NOT NULL,
	author varchar NOT NULL,
	year varchar NOT NULL,
	rating decimal
	);