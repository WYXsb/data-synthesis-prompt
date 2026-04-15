"""
Prompt templates extracted and organized from the user's appendix text.
Source: uploaded appendix text. fileciteturn0file0L1-L999

Usage:
    from prompt_templates import PROMPTS, get_prompt

    template = get_prompt("column_mapping")
    filled = template.format(N=3, schema="...")

Notes:
- All original placeholders such as {N}, {schema}, {question}, {sql}, {knowledge}
  are preserved for runtime formatting.
- Use str.format(...) to inject variables.
"""


def get_prompt(name: str) -> str:
    """Return a prompt template by name."""
    try:
        return PROMPTS[name]
    except KeyError as e:
        available = ", ".join(sorted(PROMPTS))
        raise KeyError(f"Unknown prompt template: {name}. Available: {available}") from e


COLUMN_MAPPING_PROMPT = """You are a data analyst generating training data for text-to-SQL.

TASK:
Generate {N} knowledge-question-SQL triples.

Knowledge Type:
column mapping (a concept maps to one or more columns)

Definition:
A business concept corresponds directly to one or more database columns.

Requirements:
1. Identify one column-mapping knowledge from the schema.
2. Generate a question that requires this mapping.
3. Generate a correct SQL query.
4. Use only schema information.
5. Do not invent tables or columns.

Triple Examples:
[
    {{
        "question": "List the names and mailing addresses of all schools.",
        "knowledge": "Mailing address corresponds to Zip, Street, City, State",
        "sql": "SELECT School, Zip, Street, City, State FROM schools"
    }},
    {{
        "question": "Show the usernames and their join dates.",
        "knowledge": "join date corresponds to account_created_at",
        "sql": "SELECT username, account_created_at FROM users"
    }},
    {{
        "question": "What are the titles and release years of all films?",
        "knowledge": "film corresponds to movies table; release year corresponds to release_date",
        "sql": "SELECT movie_title, release_date FROM movies"
    }}
]

SCHEMA:
{schema}

Now, please Generate {N} knowledge-question-SQL triples. ONLY OUTPUT JSON ARRAY FORMAT.
"""


TERM_DEFINITION_PROMPT = """You are a data analyst generating training data for text-to-SQL.

TASK:
Generate {N} knowledge-question-SQL triples.

Knowledge Type:
term definition (a term maps to a value meaning)

Definition:
A business/domain term corresponds to a specific column value.

Requirements:
1. Identify one term-definition knowledge from the schema.
2. Generate a question using the business term.
3. Generate the SQL query using the correct value filter.
4. Use only schema information.
5. Do not invent tables or columns.

Triple Examples:
[
    {{
        "question": "For season 9, episode 17 of the show Law and Order, how many roles have been included in the credit?",
        "knowledge": "Law and Order refers to series = 'Law and Order'; included in the credit refers to credited = 'true'",
        "sql": "SELECT COUNT(T2.role) FROM Episode AS T1 INNER JOIN Credit AS T2 ON T1.episode_id = T2.episode_id WHERE T1.series = 'Law and Order' AND T1.season = 9 AND T1.episode = 17 AND T2.credited = 'true'"
    }},
    {{
        "question": "List down the product IDs and names that include the word \\"Outdoor\\".",
        "knowledge": "names that include the word \\"Outdoor\\" refer to `Product Name` LIKE '%Outdoor%'",
        "sql": "SELECT ProductID, T FROM (SELECT ProductID, CASE WHEN `Product Name` LIKE '%Outdoor%' THEN `Product Name` ELSE NULL END AS T FROM Products) WHERE T IS NOT NULL ORDER BY T DESC"
    }},
    {{
        "question": "What are the names of the person that were not credited at the end of episode tt0629391?",
        "knowledge": "not credited refers to credited = 'false'; episode tt0629391 refers to episode_id = 'tt0629391'",
        "sql": "SELECT T2.name FROM Credit AS T1 INNER JOIN Person AS T2 ON T2.person_id = T1.person_id WHERE T1.credited = 'false' AND T1.episode_id = 'tt0629391'"
    }}
]

SCHEMA:
{schema}

Now, please Generate {N} knowledge-question-SQL triples. ONLY OUTPUT JSON ARRAY FORMAT.
[
    {{
        "question": "...",
        "knowledge": "...",
        "sql": "..."
    }}
]
"""


METRIC_DEFINITION_PROMPT = """You are a data analyst generating high-quality training data for text-to-SQL.

TASK:
Generate {N} knowledge-question-SQL triples.

Knowledge Type:
metric definition knowledge

Definition:
A metric definition knowledge item describes a domain-specific analytical metric.
The metric should be expressed as a professional or business term, and this
term must be defined by aggregation or computation over one or more columns.
The metric is not a direct column name, but a higher-level concept derived from
database fields.

Requirements for each triple:
1. Define ONE domain-specific metric term.
2. The knowledge must follow this style:
   "Metric term" = formula over columns
3. The metric term should represent a meaningful analytical concept, such as a
   rate, ratio, score, average, gap, or derived indicator.
4. The metric term must not be a direct restatement of a column name.
5. The knowledge should focus on the metric definition only.
6. Do NOT include column mapping knowledge or term-value filtering knowledge
   unless they are necessary as part of the metric formula itself.
7. The question should ask about the metric naturally, as a real analytical
   question.
8. The SQL must correctly implement the metric definition.
9. Use only the provided schema.

Triple Examples:
[
    {{
        "question": "Which school has the highest eligible free rate for K-12 students?",
        "knowledge": "\\"Eligible free rate for K-12\\" = SUM(Free Meal Count (K-12)) / SUM(Enrollment (K-12))",
        "sql": "SELECT school_name FROM schools ORDER BY CAST(`Free Meal Count (K-12)` AS REAL) / `Enrollment (K-12)` DESC LIMIT 1"
    }},
    {{
        "question": "What is the excellence rate of each school?",
        "knowledge": "\\"Excellence rate\\" = NumGE1500 / NumTstTakr",
        "sql": "SELECT school_name, CAST(NumGE1500 AS REAL) / NumTstTakr FROM satscores"
    }},
    {{
        "question": "Which department has the highest complaint resolution rate?",
        "knowledge": "\\"Complaint resolution rate\\" = COUNT(resolved complaints) / COUNT(all complaints)",
        "sql": "SELECT department_name FROM complaints GROUP BY department_name ORDER BY CAST(SUM(CASE WHEN complaint_status = 'Resolved' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) DESC LIMIT 1"
    }},
    {{
        "question": "What is the on-time response rate of each company?",
        "knowledge": "\\"On-time response rate\\" = COUNT(responses sent on time) / COUNT(all responses)",
        "sql": "SELECT company_name, CAST(SUM(CASE WHEN julianday(`Date sent to company`) - julianday(`Date received`) <= 15 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) FROM complaints GROUP BY company_name"
    }}
]

SCHEMA:
{schema}

Now generate {N} knowledge-question-SQL triples.

ONLY OUTPUT JSON ARRAY FORMAT.
[
    {{
        "question": "...",
        "knowledge": "...",
        "sql": "..."
    }}
]
"""


LEVEL1_SYSTEM_PROMPT = """You are a strict annotator for NLQ-to-SQL question quality levels.

Task: decide whether the question is Level 1 (illogical / nonsensical intent).

Definition of Level 1:
- The question is logically invalid or unnatural as a real user request.
- Typical signals:
  * Doing arithmetic on identifier-like fields (id, key, code, uuid), e.g.,
    id1 - id2, id + 3.
  * Treating categorical strings as numeric measures, e.g., "name > 5",
    "city - country".
  * Asking for meaningless comparisons/differences between unrelated
    attributes without a real metric.

Important:
- A question can be executable but still Level 1 if the intent is nonsensical.

Output format:
Return ONLY JSON: {{"is_level1": true/false}}
No extra text.
"""


LEVEL1_USER_PROMPT = """Decide if the question is Level 1 (illogical / nonsensical intent).

Few-shot examples:

Q: "Compute the difference between user_id 12 and user_id 80."
A: {{"is_level1": true}}

Q: "What is the city name minus the country name for each record?"
A: {{"is_level1": true}}

Q: "List the names of players whose jumping is greater than 80."
A: {{"is_level1": false}}

Q: "How many orders did each customer place in 2024?"
A: {{"is_level1": false}}

Now classify:

Q: "{question}"
A:
"""


LEVEL23_SYSTEM_PROMPT = """You are a strict annotator for domain-relatedness levels in NLQ-to-SQL datasets.

Your task is to classify a question into either Level 2 or Level 3.

Definitions:

Level 2 (Structure-driven relevance):
- The question is directly triggered by existing columns.
- It may include filtering, sorting, aggregation, GROUP BY, JOIN, ranking, or subqueries.
- SQL can be complex.
- However, no new business metric or domain-defined concept is constructed.
- The query stays within raw column operations.

Level 3 (Concept-driven relevance):
- The question requires constructing or referring to a domain-level concept or business metric.
- The concept exists prior to raw database columns.
- It typically involves a defined formula, ratio, composite indicator, or business rule.
- SQL is only used to implement that higher-level concept.

Important clarifications:
- SQL complexity alone does NOT imply Level 3.
- GROUP BY, JOIN, ranking, or time-series aggregation alone are still Level 2.
- A ratio is Level 3 ONLY if it represents a domain-defined metric (e.g., retention rate, ROI, load factor).
- If the question can be asked simply by reading column names, it is Level 2.
- Ask yourself: "Does this require domain knowledge beyond raw columns?"

Output format:
Return ONLY a JSON object:
{{"level": "level2" or "level3", "reason": "<one concise sentence>"}}
No extra text.
"""


LEVEL23_USER_PROMPT = """Classify the following question as Level 2 or Level 3.

SQL:
{sql}

Question:
"{question}"

Few-shot examples:

Example 1
SQL: SELECT name FROM students WHERE age = 20;
Question: "Show the names of students whose age is 20."
Answer: {{"level":"level2","reason":"Simple filter directly driven by existing columns."}}

Example 2
SQL: SELECT region, SUM(revenue) FROM sales GROUP BY region;
Question: "What is the total revenue per region?"
Answer: {{"level":"level2","reason":"Group-by aggregation but no domain-specific concept construction."}}

Example 3
SQL: SELECT SUM(retained_customers) * 1.0 / SUM(total_customers) FROM sales;
Question: "What is the customer retention rate?"
Answer: {{"level":"level3","reason":"Constructs a domain-defined metric (retention rate) from raw fields."}}

Example 4
SQL: SELECT NumGE1500 * 1.0 / NumTstTakr FROM exams;
Question: "What is the excellence rate?"
Answer: {{"level":"level3","reason":"Defines a business metric based on a domain-specific formula."}}

Now classify:

Answer:
"""


SQL_GENERATION_PROMPT = """# ROLE
You are an expert in translating natural language questions into SQLite SQL queries.

You are provided with:
1. A natural language question
2. The database schema
3. Optional domain knowledge

Your goal is to generate a correct and executable SQL query.

# INSTRUCTIONS

Follow these rules strictly:

1. Only use tables and columns that appear in the provided schema.
2. Do NOT invent or assume any table or column names.
3. If multiple tables are required, use proper JOIN conditions based on the schema.
4. Ensure the SQL query is syntactically valid and executable.
5. Use table aliases when appropriate to improve readability.
6. Apply filtering conditions using WHERE when necessary.
7. Use aggregation functions (COUNT, MAX, MIN, AVG, SUM) if required by the question.
8. Use ORDER BY and LIMIT if the question asks for highest, lowest, top, etc.
9. The SQL query must be complete and executable.

# SQL GENERATION PROCESS

Before writing the final SQL query:

1. Identify the columns required to answer the question.
2. Identify the tables containing those columns.
3. Determine necessary JOIN relationships based on the schema.
4. Apply appropriate filtering or aggregation conditions.

Then generate the final SQL query.

# OUTPUT FORMAT

Return ONLY the SQL query inside a SQL code block.

Example:

```sql
SELECT p.name, p.description
FROM photo_type p
JOIN specobj s ON p.value = s.bestobjid
WHERE s.class = 'STAR';
```

Do not output explanations.
Do not output any text outside the SQL code block.

# INPUT

Question:
{question}

Database Schema:
{schema}

Optional Knowledge:
{knowledge}

# OUTPUT
"""


SQL_NEIGHBORHOOD_SYSTEM_PROMPT = """You are an expert Text-to-SQL data synthesis assistant.

Your task is to generate high-quality NLQ-SQL pairs under explicit SQL template
guidance.

You will be given:
1. the original natural language question,
2. the original SQL query,
3. the original SQL template,
4. a target SQL template,
5. the database schema,
6. optional domain knowledge.

Your goal is to generate a new NLQ-SQL pair such that:
- the new question remains semantically close to the original,
- the new SQL follows the target template as closely as possible,
- the new SQL reflects a meaningful structural variation,
- the new SQL is valid and consistent with the schema.

Constraints:
- Do not invent tables or columns.
- Do not produce trivial paraphrases of the original pair.
- Prefer meaningful structural changes (e.g., aggregation, filtering,
  grouping, ordering, subqueries) guided by the target template.

Return strictly valid JSON in the following format:
{{
  "pairs": [
    {{
      "question": "...",
      "sql": "..."
    }}
  ]
}}

Do not output explanations.
"""


SQL_NEIGHBORHOOD_USER_PROMPT = """[Original Question]
{origin_question}

[Original SQL]
{origin_sql}

[Original SQL Template]
{origin_template}

[Target SQL Template]
{target_template}

[Schema]
{schema}

[Knowledge]
{knowledge}

Generate one new NLQ-SQL pair that:
1. is semantically close to the original question,
2. follows the target SQL template,
3. reflects a meaningful structural variation,
4. is valid under the schema.

Return JSON only.
"""


QUESTION_REWRITE_SYSTEM_PROMPT = """You are a high-quality NLQ rewriting engine for Text-to-SQL datasets.

Your task: Rewrite the original question into {n} diverse, natural, human-like
variants that EXACTLY match the target SQL semantics.

Core Rules (Non-Negotiable):
1. Semantic Fidelity: Every rewritten question must 100% match the SQL's logic
   (preserve filtering, aggregation, grouping, ordering, comparison, limit,
   joins, etc.).
2. No Trivial Rewrites: Do NOT just replace 1-2 words; change sentence
   structure, phrasing, and style.
3. No Schema Leaks: Do NOT mention table names, column names, "SQL",
   "database", or "schema" unless naturally required.
4. No Extra/Removed Content: Do NOT add new constraints/entities or omit
   critical conditions from the SQL.

Diversity Requirements (Enforced):
- Use different sentence structures (simple, compound, complex).
- Mix interrogative (Who/Which/Find) and imperative (List/Show) forms.
- Vary how you phrase conditions/aggregations (e.g., "not in Australia" vs.
  "outside Australia" vs. "territories other than Australia").
- Alternate between concise and slightly descriptive formulations.
- Avoid always starting with the same pattern (don't repeat "Which..." or
  "Who..." every time).

Output Format (Strict JSON Only):
{{
  "rewritten_questions": [
    "...",
    "...",
    "..."
  ]
}}

EXAMPLES:

Example 1:
Target SQL:
SELECT s.BusinessEntityID FROM SalesPerson s JOIN SalesTerritory t ON s.TerritoryID = t.TerritoryID WHERE t.Name <> 'Australia';

Rewritten Questions:
[
"List the identifiers of salespeople who are not assigned to Australia.",
"Show the unique IDs of sales representatives working outside the Australian region.",
"Provide the ID numbers of sales staff associated with non-Australian territories."
]


Example 2:
Target SQL:
SELECT s.BusinessEntityID FROM SalesPerson s JOIN SalesTerritory t ON s.TerritoryID = t.TerritoryID WHERE t.Name = 'Australia';

Rewritten Questions:
[
"List the identifiers of salespeople assigned to Australia.",
"Show the unique IDs of sales representatives working in the Australian region.",
"Provide the ID numbers of sales staff associated with the Australian territory."
]
"""


QUESTION_REWRITE_USER_PROMPT = """Generate exactly {n} rewritten questions for the target SQL.

Original Question:
{question}

Target SQL:
{sql}

Schema:
{schema}

Optional Knowledge:
{knowledge}

Final Requirements Recap:
1. All rewritten questions must EXACTLY match the target SQL semantics.
2. No trivial word swaps--change sentence structure and style.
3. Questions must be diverse from each other and the original.
4. Use natural, human-like language (no machine translation).
5. Do NOT mention schema/table/column/SQL unless necessary.
6. Do NOT generate explanations.
7. Return strict JSON only.

Return JSON only:
{{
  "rewritten_questions": [
    "...",
    "...",
    "..."
  ]
}}
"""


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


if __name__ == "__main__":
    print("Available prompt templates:")
    for key in sorted(PROMPTS):
        print(f"- {key}")
