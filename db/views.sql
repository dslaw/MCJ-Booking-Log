create view charges_t as (
    select
        booking_id,
        cast(record ->> 'bail' as integer) as bail,
        lower(record ->> 'level') as level,
        lower(record ->> 'charge') as charge,
        lower(record ->> 'description') as description,
        lower(record ->> 'charge_authority') as charge_authority
    from (
        select
            booking_id,
            jsonb_array_elements(recorded) as record
        from charges
    ) as t
);
