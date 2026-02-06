rootProject.name = "moneylane"

include("bootstrap")
include("modules:transaction")
include("modules:budget")
include("modules:insight")
include("modules:auth:auth-common")
include("modules:auth:auth-local")
include("modules:auth:auth-supabase")
include("shared:kernel")
include("shared:contracts")
include("common:exception")
include("common:util")
