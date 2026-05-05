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


COLUMN_MAPPING_PROMPT = """
You are a data analyst generating training data for text-to-SQL.

TASK:
Generate {N} knowledge–question–SQL triples.

Knowledge type:
column mapping (a concept maps to columns)

Definition:
A business concept corresponds directly to one or more database columns.

Triple Examples:
[
    {
        "question": "State the names and full communication address of high schools in Monterey which has more than 800 free or reduced price meals for ages 15-17? ",
        "knowledge": "Full communication address should include Zip, Street, City, State",
        "sql": "SELECT T1.School, T1.Zip, T1.Street, T1.City, T1.State FROM schools T1 JOIN frpm T2 ON T1.CDSCode = T2.CDSCode WHERE T1.EILName = 'High School' AND T1.City = 'Monterey' AND T2.`FRPM Count (Ages 5-17)` > 800"
    },
    {
        "question": "Show the usernames and their join dates.",
        "knowledge": "join date corresponds to account_created_at",
        "sql": "SELECT username, account_created_at FROM users"
    },
    {
        "question": "What are the titles and release years of all films?",
        "knowledge": "film corresponds to movies table; release year corresponds to release_date",
        "sql": "SELECT movie_title, release_date FROM movies"
]




Requirements:
1. Identify one column-mapping knowledge from the schema.
2. Generate a question that requires this mapping.
3. Generate a correct SQL query.
4. Use only schema information.
5. Do not invent tables or columns.

SCHEMA:
{schema}

Now, please Generate {N} knowledge–question–SQL triples. ONLY OUTPUT JSON ARRAY FORMAT.
```json
[
    {
        "question": "...",
        "knowledge": "...",
        "sql": "..."
    }
]
``` 
"""

TERM_DEFINITION_PROMPT = """
You are a data analyst generating training data for text-to-SQL.

TASK:
Generate {N} knowledge–question–SQL triples.

Knowledge type:
term definition (a term maps to a value meaning)

Definition:
A business/domain term corresponds to a specific column value.

Triple Examples:
[
    {
        "question": "For season 9, episode 17 of the show Law and Order, how many roles have been included in the credit?",
        "knowledge": "Law and Order refers to series = 'Law and Order'; included in the credit refers to credited = 'true'",
        "sql": "SELECT COUNT(T2.role) FROM Episode AS T1 INNER JOIN Credit AS T2 ON T1.episode_id = T2.episode_id WHERE T1.series = 'Law and Order' AND T1.season = 9 AND T1.episode = 17 AND T2.credited = 'true'"
    },
    {
        "question": "List down the product IDs and names that include the word \"Outdoor\".",
        "evidence": "names that include the word \"Outdoor\" refer to Product Name LIKE '%Outdoor%';",
        "SQL": "SELECT ProductID, T FROM ( SELECT ProductID , CASE  WHEN `Product Name` LIKE '%Outdoor%' THEN `Product Name` ELSE NULL END AS T FROM Products ) WHERE T IS NOT NULL ORDER BY T DESC"
    },
    {
        "question": "What are the names of the person that were not credited at the end of episode tt0629391?",
        "knowledge": "not credited refers to credited = ''; episode tt0629391 refers to episode_id = 'tt0629391'",
        "sql": "SELECT T2.name FROM Credit AS T1 INNER JOIN Person AS T2 ON T2.person_id = T1.person_id WHERE T1.credited = 'false' AND T1.episode_id = 'tt0629391'"
    }
]

Requirements:
1. Identify one term-definition knowledge from the schema.
2. Generate a question using the business term.
3. Generate the SQL query using the correct value filter.
4. Use only schema information.
5. Do not invent tables or columns.

SCHEMA:
{schema}

Now, please Generate {N} knowledge–question–SQL triples. ONLY OUTPUT JSON ARRAY FORMAT.
```json
[
    {
        "question": "...",
        "knowledge": "...",
        "sql": "..."
    }
]
``` 
"""


generate_metric_definition_prompt = """
You are a data analyst generating training data for text-to-SQL.

TASK:
Generate {N} knowledge–question–SQL triple.

Knowledge type:
metric definition 

Definition:
A metric defined using aggregation or computation over columns.

Triple Examples:
[
    {
        "question": "Who is the person who appeared the most in the series? Calculate in percentage how many times he or she appeared.",
        "knowledge": "who refers to name; appear the most refers to max(count(person_id)); percentage = divide(count(person_id where max(count(person_id))), count(person_id)) * 100%",
        "sql": "SELECT T2.person_id, CAST(COUNT(T2.person_id) AS REAL) * 100 / ( SELECT COUNT(T2.person_id) AS num FROM Credit AS T1 INNER JOIN Person AS T2 ON T2.person_id = T1.person_id ) AS per FROM Credit AS T1 INNER JOIN Person AS T2 ON T2.person_id = T1.person_id GROUP BY T2.person_id ORDER BY COUNT(T2.person_id) DESC LIMIT 1"
    },
    {
        "question": "What is the social number of the client who has the longest delay in his/her complaint? Calculate the days of delay and state the company's response to the consumer.",
        "knowledge": "social number refers to social; longest delay = max(subtract(Date sent to company, Date received)); days of delay = subtract(Date sent to company, Date received); company's response refers to 'Company response to consumer'",
        "sql": "SELECT T1.social , 365 * (strftime('%Y', T2.`Date sent to company`) - strftime('%Y', T2.`Date received`)) + 30 * (strftime('%M', T2.`Date sent to company`) - strftime('%M', T2.`Date received`)) + (strftime('%d', T2.`Date sent to company`) - strftime('%d', T2.`Date received`)), T2.`Company response to consumer` FROM client AS T1 INNER JOIN events AS T2 ON T1.client_id = T2.Client_ID ORDER BY 365 * (strftime('%Y', T2.`Date sent to company`) - strftime('%Y', T2.`Date received`)) + 30 * (strftime('%M', T2.`Date sent to company`) - strftime('%M', T2.`Date received`)) + (strftime('%d', T2.`Date sent to company`) - strftime('%d', T2.`Date received`)) DESC LIMIT 1"
    },
    {
        "question": "What is the percentage of the ratings were rated by user who was a subcriber?",
        "knowledge": "user is a subscriber refers to user_subscriber = 1; percentage of ratings = DIVIDE(SUM(user_subscriber = 1), SUM(rating_score)) as percent;",
        "sql": "SELECT CAST(SUM(CASE WHEN user_subscriber = 1 THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*) FROM ratings"
    },
    {
        "question": "How much higher is the average rating score of the movie \"Innocence Unprotected\" than the movie \"When Will I Be Loved\"?",
        "knowledge": "Innocence Unprotected' and 'When Will I Be Loved' are movie_title; Average rating score = Divide(Sum(rating_score), Count(rating_id));",
        "sql": "SELECT SUM(CASE WHEN T2.movie_title = 'Innocence Unprotected' THEN T1.rating_score ELSE 0 END) / SUM(CASE WHEN T2.movie_title = 'Innocence Unprotected' THEN 1 ELSE 0 END) - SUM(CASE WHEN T2.movie_title = 'When Will I Be Loved' THEN T1.rating_score ELSE 0 END) / SUM(CASE WHEN T2.movie_title = 'When Will I Be Loved' THEN 1 ELSE 0 END) FROM ratings AS T1 INNER JOIN movies AS T2 ON T1.movie_id = T2.movie_id"
    }
]


Requirements:
1. Define one meaningful metric using schema columns.
2. Generate a question asking for that metric.
3. Generate the SQL query implementing the formula.
4. Use aggregation when appropriate.
5. Use only schema information.

SCHEMA:
{schema}

Now, please Generate {N} knowledge–question–SQL triples. ONLY OUTPUT JSON ARRAY FORMAT.
```json
[
    {
        "question": "...",
        "knowledge": "...",
        "sql": "..."
    }
]
``` 
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


SQL_NEIGHBORHOOD_PROMPT =  """
You are an expert in a specific domain.
You are provided with:
    1. An SQL query template
    2. A question that the query needs to answer
    3. The schema of the relevant database


Your task is to:
    1.Strictly use the information from the provided schema to generate {N} DISTINCT pairs of SQLite query and natural language question(NLQ). Ensure that all necessary table names, column names, and clauses (such as FROM and JOIN) come from the schema only.
    2.Avoid introducing any table names, column names, or other elements that are not explicitly defined in the schema.
    3.The generated {N} NLQ-SQL pairs need to fit the SQL query template.
    4.the conditions should be much complex.
    5.Keep the output json format.
    6.Refer to the database schema, and ensure all SQLs in the {N} pairs are DISTINCT.
    7.When information from multiple tables is needed, prefer explicit JOIN ... ON clauses to introduce fields from related tables, rather than using IN subqueries or equality-based subqueries, unless a subquery is strictly necessary.
Example:
Input:
SQL Query Template: SELECT col_1, col_2  WHERE col_3 = value_0;
Question: What are the names and descriptions of the different types of photos associated with objects in the astrophysical classifications from the specobj table?
Database Schema:
CREATE TABLE photo_type (
    value number Example Values[(6,), (2,), (4,)],
    name text Example Values[('GHOST',), ('STAR',), ('NOTATYPE',)],
    description text Example Values[('Sky: Blank sky spectrogram (no objects in this arcsecond area).',), ('Trail: A satellite or asteroid or meteor trail. (not yet used)',), ('Unknown: Object type is not known.',)],
    primary key (value),
    foreign key (value) references photoobj(type),
    foreign key (value) references neighbors(neighbortype)
)
CREATE TABLE specobj (
    specobjid number ,
    bestobjid number ,
    plateid number Example Values[(Decimal('8253972328771233792'),), (Decimal('8255098229097506816'),), (Decimal('8034421845460527104'),)],
    scienceprimary number Example Values[(1,)],
    segue2primary number Example Values[(0,), (1,)],
    survey text Example Values[('boss',), ('sdss',), ('eboss',)],
    programname text Example Values[('boss',), ('legacy',), ('eboss',)],
    mjd number ,
    plate number ,
    fiberid number ,
    special_target1 number ,
    segue2_target1 number ,
    segue2_target2 number ,
    ancillary_target1 number ,
    ra number ,
    dec number ,
    z number ,
    zerr number ,
    zwarning number ,
    class text Example Values[('GALAXY',), ('STAR',), ('QSO',)],
    subclass text Example Values[(None,), ('BROADLINE',), ('STARFORMING',)],
    veldisp number,
    veldisperr number ,
    loadversion number,
    primary key (specobjid),
    foreign key (bestobjid) references photoobj(objid)
)
Output:
{{
  "pairs": [
    {{
      "question": "What are the names and descriptions of photo types where the object class is 'STAR'?",
      "sql": "SELECT p.name, p.description FROM photo_type p JOIN specobj s ON p.value = s.bestobjid WHERE s.class = 'STAR';"
    }},
    {{
      "question": "Retrieve the name and program name of photo types where the subclass is 'BROADLINE'.",
      "sql": "SELECT p.name, s.programname FROM photo_type p JOIN specobj s ON p.value = s.bestobjid WHERE s.subclass = 'BROADLINE';"
    }},
    {{
      "question": "What are the names and program names of photo types where the object class is 'QSO'?",
      "sql": "SELECT p.name, s.programname FROM photo_type p JOIN specobj s ON p.value = s.bestobjid WHERE s.class = 'QSO';"
    }},
    {{
      "question": "What are the names and program names of photo types where the RA (right ascension) is greater than 130?",
      "sql": "SELECT p.name, s.programname FROM photo_type p JOIN specobj s ON p.value = s.bestobjid WHERE s.ra > 130;"
    }}
  ]
}}

Now, it's your turn.
Input:
SQL Query Template: {skeleton}
Question: {question}
Knowledge:{knowledge}
Database Schema: 
{schema}
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
    "sql_neighborhood": SQL_NEIGHBORHOOD_PROMPT,

}


if __name__ == "__main__":
    print("Available prompt templates:")
    for key in sorted(PROMPTS):
        print(f"- {key}")
