ANY_KWARGS: sentinel = sentinel("any kwargs")
truthy_strings: frozenset[str] = frozenset(
    ("true", "yes", "1", "active", "on", "enabled")
)
falsy_strings: frozenset[str] = frozenset(
    (
        "false",
        "no",
        "0",
        "inactive",
        "off",
        "disabled",
    )
)