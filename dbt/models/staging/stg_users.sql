select
    id,
    name,
    created_at
from {{ source('operational', 'users') }}
