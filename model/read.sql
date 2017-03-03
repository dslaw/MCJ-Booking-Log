-- name: query-inmates
-- Get inmates with features.
select
    booking.jail_id,
    booking.id as booking_id,
    (coalesce(arrests.arrest_date::date, booking.orig_booking_date::date) - inmates.dob) / 365 as age,
    t.race,
    lower(inmates.sex) as sex,
    case inmates.occupation
        when '' then null
        else lower(inmates.occupation)
    end as occupation
from booking as booking
join arrests on arrests.booking_id = booking.id
join inmates on inmates.booking_id = booking.id
join (
    select
        case lower(race)
          when 'v' then 'a' -- "vietnamese"
          when 'k' then 'a' -- "korean"
          else lower(race)
        end as race,
        booking_id
    from inmates
) as t on t.booking_id = booking.id;

-- name: query-charges
-- Get expanded inmate charges.
select * from charges_t;
