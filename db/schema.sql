create table booking (
    id serial primary key,
    jail_id varchar(9) unique, /* natural key */
    orig_booking_date timestamp,
    latest_charge_date timestamp,
);

create table arrests (
    id serial primary key,
    booking_id integer unique,
    arrest_date timestamp,
    agency varchar(256),
    location varchar(256),
    foreign key (booking_id) references booking(id)
);

create table inmates (
    id serial primary key,
    booking_id integer unique,
    name varchar(256),
    dob date,
    eye_color char(3),
    hair_color char(3),
    height varchar(8),
    weight integer,
    race char(1),
    sex char(1),
    occupation varchar(256),
    foreign key (booking_id) references booking(id)
);

/* As the same charge can appear multiple times, hold all associated
 * charges as a single array of maps. Expected form of each map is:
 * {charge: text,
 *  description: text,
 *  bail: integer,
 *  charge_authority: text,
 *  severity_level: character}
 */
create table charges (
    id serial primary key,
    booking_id integer unique,
    recorded jsonb not null,
    foreign key (booking_id) references booking(id)
);


create index jail_id_idx on booking (jail_id);
create index arrests_booking_fk_idx on arrests (booking_id);
create index inmates_booking_fk_idx on inmates (booking_id);
create index charges_booking_fk_idx on charges (booking_id);

