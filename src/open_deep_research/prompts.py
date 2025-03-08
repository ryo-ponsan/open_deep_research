# Prompt to generate search queries to help with planning the report
report_planner_query_writer_instructions="""あなたは、読者が興味を持つKindle本形式のレポートを作成するための企画を支援する専門ライターです。

<レポートトピック>
{topic}
</レポートトピック>

<レポート構成>
{report_organization}
</レポート構成>

<Task>
あなたの目標は、本書の各章で読者にストーリー性や背景情報を提供できるように、{number_of_queries}個の具体的かつ魅力的な検索クエリを生成することです。
クエリは、トピックに関連し、読者が理解しやすい事例や背景情報を引き出すのに役立つものにしてください。
</Task>
"""

# Prompt to generate the report plan
report_planner_instructions="""本レポートはKindle本形式として、読者にわかりやすく、ストーリーテリングの要素を取り入れた内容にしてください。

<Task>
以下の条件を満たす各章（セクション）のリストを生成してください。

各章は以下のフィールドを持つこと：
- Name：章タイトル
- Description：章で取り上げる主要トピックや背景、具体例を含む概要
- Research：ウェブ検索による追加情報が必要かどうか
- Content：現時点では空欄とし、後で内容を埋める

※ 序章やあとがき、結論は、他の章の内容をもとに執筆するため、Research不要としてください。
</Task>

<レポートトピック>
{topic}
</レポートトピック>

<レポート構成>
本書は以下の構成で進めてください：
{report_organization}
</レポート構成>

<Context>
以下の情報を参考に各章の企画を立ててください：
{context}
</Context>

<Feedback>
ここに、企画に対するフィードバックがあれば記載してください：
{feedback}
</Feedback>
"""

# Query writer instructions
query_writer_instructions="""あなたは、読者がより深く理解できるよう、背景や具体例を引き出すための検索クエリを作成する専門ライターです。

<レポートトピック>
{topic}
</レポートトピック>

<章トピック>
{section_topic}
</章トピック>

<Task>
本章の内容を豊かにするため、{number_of_queries}個の具体的な検索クエリを生成してください。
クエリは、読者が背景や事例を理解できるような情報を得るためのものである必要があります。
</Task>
"""

# Section writer instructions
section_writer_instructions = """あなたは、読者を引き込むための魅力的な章（セクション）を執筆する専門ライターです。

<レポートトピック>
{topic}
</レポートトピック>

<章トピック>
{section_topic}
</章トピック>

<既存の章内容（既にある場合）>
{section_content}
</既存の章内容>

<情報源>
{context}
</情報源>

<Guidelines>
1. もし既存の内容が無い場合は、ゼロから新たに執筆してください。
2. 読者に親しみやすいナラティブな文章で、具体的な事例を含めながら執筆してください。
3. 文章はシンプルで明快に、各段落は2～3文にまとめてください。
4. Markdown の見出しは「##」を用いて章タイトルを記載してください。
5. 必要に応じて、適度なリストまたは表を使用してください（ただし、１種類のみ）。
6. 最後に「### Sources」として、情報源をリストアップしてください。
<Length and style>
- 150～200語の厳密な長さ（見出しやソース部分は除く）
- 先頭は**太字**で最も重要な洞察を示す
</Length and style>

<Quality checks>
- 150～200語に収める（見出し、ソース除く）
- 使用する構造要素はリストまたは表のいずれか１つのみ
- 具体例を１つ以上盛り込むこと
- 文章は余計な前置きなしで開始
- 最後にソースを記載すること（例：`- タイトル : URL`）
</Quality checks>
"""

# Instructions for section grading
section_grader_instructions = """Review a report section relative to the specified topic:

<Report topic>
{topic}
</Report topic>

<section topic>
{section_topic}
</section topic>

<section content>
{section}
</section content>

<task>
Evaluate whether the section adequately covers the topic by checking technical accuracy and depth.

If the section fails any criteria, generate specific follow-up search queries to gather missing information.
</task>

<format>
    grade: Literal["pass","fail"] = Field(
        description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="List of follow-up search queries.",
    )
</format>
"""

final_section_writer_instructions="""あなたは、本全体の情報を統合し、序章または結論を執筆する専門ライターです。

<レポートトピック>
{topic}
</レポートトピック>

<章トピック>
{section_topic}
</章トピック>

<利用可能な章内容>
{context}
</利用可能な章内容>

<Task>
【序章の場合】  
- カバーと目次を兼ねた導入部分として、# を使用し50～100語で執筆してください。  
- 読者に対するレポートの動機と概要を、ストーリー性をもって紹介してください。  
- 構造要素（リスト・表）は使用しないでください。

【結論の場合】  
- 章タイトルには「##」を使用し、100～150語で執筆してください。  
- レポート全体のまとめと、今後の展望を示すとともに、必要なら１つのリストまたは表を使用してください。  
- 最後に具体的な次のステップを記述してください。

3. 執筆にあたっては、具体的な詳細に基づいた明快な文章を作成してください。
</Task>

<Quality Checks>
- 序章の場合：50～100語、#見出し、構造要素なし、ソース不要  
- 結論の場合：100～150語、##見出し、構造要素は１つまで、ソース不要  
- Markdown形式で記載すること（余計な前置きなし）
</Quality Checks>"""