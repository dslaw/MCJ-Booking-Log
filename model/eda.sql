select distinct on (agency) agency from arrests;


/* Race */
select distinct race from inmates;

select race, count(race)
from inmates
group by race
having race in ('H', 'W', 'B', 'O', 'A');

select name, race
from inmates
where not race in ('H', 'W', 'B', 'O', 'A');

select *
from inmates
where race = 'A';
/* It looks like ``V`` is being used for Vietnamese,
 * ``K`` for Korean and ``A`` for Asian. */

select *
from inmates
where race = 'O';
/* And other is _not_ being used to include Asians. Except for one person who
 * slipped through. */


/* Age */
create temp view ages as (
    select
        inmates.booking_id as booking_id,
        (arrest_date::date - dob) / 365 as age
    from inmates
    join arrests on arrests.booking_id = inmates.booking_id
);


select min(age), max(age) from ages;

select age, count(*)
from ages
group by age
order by age;


/* Sex */
select distinct on (sex) sex from inmates;

select sex, count(*)
from inmates
group by sex;

/* Age and sex */
select age, sex, count(*) as n
from inmates
join ages on ages.booking_id = inmates.booking_id
group by age, sex
order by age;


/* Occupation */
select distinct lower(occupation)
from inmates;

select distinct occupation
from inmates
where lower(occupation) like '%nempl%'
or lower(occupation) like 'unem%';
/* Catches (no false positives):
 *  unemloyed
 *  unemployoed
 *  enemployed
 *  unemplolyed
 *  unemployed
 */

/* Other unemployed variants:
 *  none
 *  never had a job
 *  nothing
 *  non
 *  homeless
 */

/* May count depending on definition:
 *  retired
 *  on disability
 *  diabled
 *  disable
 *  dissabld
 *
 *  student
 *  
 *  stay at home dad
 *  stay at home mom
 *  stay home mom
 */


/* Bail */
create temp view records as (
    select
        booking_id,
        jsonb_array_elements(recorded) ->> 'bail' as bail,
        jsonb_array_elements(recorded) ->> 'level' as level,
        jsonb_array_elements(recorded) ->> 'description' as description,
        jsonb_array_elements(recorded) ->> 'charge_authority' as authority
    from charges
);

select min(bail::integer), max(bail::integer)
from records;

select avg(total_bail) from (
    select sum(bail::integer) as total_bail
    from records
    group by booking_id
) as t;


select level, count(*)
from records
group by level;

select distinct description from records where level = 'X';


select authority, count(*)
from records
group by authority
having authority <> '';


select count(distinct lower(description))
from records;
