RULESET_PROPS = "id,ruleset_name,ruleset_type,ruleset_public"
RULESET_VARIABLE_PROPS = "id,ruleset_id,var_name,var_class,var_author,var_updated"
RULESET_VARIABLE_VALUE_PROP = "var_value"


def ruleset_variable_props(include_var_value: bool) -> str:
    if include_var_value:
        return f"{RULESET_VARIABLE_PROPS},{RULESET_VARIABLE_VALUE_PROP}"
    return RULESET_VARIABLE_PROPS
