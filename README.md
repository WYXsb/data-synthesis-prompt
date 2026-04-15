# data-synthesis-prompt

``` python
PROMPTS = {
    # Explicit knowledge generation
    "column_mapping": COLUMN_MAPPING_PROMPT,
    "term_definition": TERM_DEFINITION_PROMPT,
    "metric_definition": METRIC_DEFINITION_PROMPT,

    # Domain-relatedness judgment
    "level1_system": LEVEL1_SYSTEM_PROMPT,
    "level1_user": LEVEL1_USER_PROMPT,
    "level23_system": LEVEL23_SYSTEM_PROMPT,
    "level23_user": LEVEL23_USER_PROMPT,

    # SQL generation
    "sql_generation": SQL_GENERATION_PROMPT,

    # SQL semantic neighborhood generation
    "sql_neighborhood_system": SQL_NEIGHBORHOOD_SYSTEM_PROMPT,
    "sql_neighborhood_user": SQL_NEIGHBORHOOD_USER_PROMPT,

    # Question rewriting
    "question_rewrite_system": QUESTION_REWRITE_SYSTEM_PROMPT,
    "question_rewrite_user": QUESTION_REWRITE_USER_PROMPT,
}
```
