select
    name,
    count(*) as user_count,
    min(created_at) as first_created_at,
    max(created_at) as last_created_at
from {{ ref('stg_users') }}
group by name
