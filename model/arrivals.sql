-- name: query-arrivals
-- Get daily arrival counts.
with counts as (
    select
        orig_booking_date::date as booking_date,
        count(*) as n
    from booking
    group by orig_booking_date::date
    order by orig_booking_date::date
)
select
    t.series as booking_date,
    counts.n
from (
    select
        generate_series(
            min(counts.booking_date),
            max(counts.booking_date),
            '1 day'::interval) as series
    from counts
) as t
left outer join counts on t.series = counts.booking_date;
