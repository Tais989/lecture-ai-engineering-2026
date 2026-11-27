# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：`glossary_search_glossary`
- STEP 2 の [tool call]：`glossary_search_glossary({'query': '3レベル'})`
- STEP 3 の [tool call]：`fetch_fetch({'url': 'https://modelcontextprotocol.io/'})`
- STEP 4 の [tool call]：`aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング', 'topics': ['general']})` の後、`aws_aws___search_documentation({'search_phrase': 'What is versioning in Amazon S3', 'topics': ['general']})`
- 気づき・疑問：
  - 設定ファイルに書き足すだけで、ツールが 1個 → 2個（fetch）→ 7個（aws）と増え、エージェント側のコードは変更不要だった。
  - ツール名は `サーバー名_ツール名` になり、aws は `aws_aws___…` と接頭辞が二重になる。
  - 日本語の検索結果が弱かったため、モデルが英語で再検索した（ツール呼び出し2回、モデル応答3回）。
  - 入力トークンは、glossary 709、fetch 2,224、aws 11,292 と、ツールが増えるほど大きくなった。
  - 疑問：外部サーバーに質問が送られるため、機密情報を含む質問をどう扱うべきか。
- 気づき・疑問：
  - 設定ファイル（`app/mcp_servers.json`）に書き足すだけで、エージェント側のコードを変えずにツールが増えた（一覧：1個 → 2個 → 7個）。
  - ツール名は「サーバー名_ツール名」の形になる。AWSは `aws_aws___…` と `aws` が重なる（設定名の `aws` に、サーバー側のツール名の `aws___` が続くため）。
  - AWSの検索では、日本語の検索語（1回目）で関連の薄い記事が先頭に返り、モデルが英語の検索語に言い換えて再検索した。呼び出しは2回、モデル応答は3回だった。
  - 入力トークンは、glossary が709、fetch が2,224、aws が11,292だった。ツールが増えるほど、モデルに渡す説明文とツールの結果が増える。
  - 疑問：外部サーバー（aws）には質問の内容が送られる。機密を含む質問をしてよいかは、使う前に確認が必要だと思った。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎
- やったこと：`app/mcp_server.py` の TODO の下に `server.tool()(tools.get_lecture_summary)` を1行追加し、`get_lecture_summary` を MCP ツールとして公開した。
- 結果：`--list-tools` でツールが 7個から8個になり、`glossary_get_lecture_summary` が加わった。`--trace "第2回では何を学びますか？"` で `glossary_get_lecture_summary({'lecture': 2})` が呼ばれ、第2回（ファインチューニングと LoRA）の要点で回答した（入力 5,932 / 出力 311 tokens、応答2回）。`uv run pytest -q` は 21 passed。
- 気づき・疑問：エージェント側を変えず、サーバーに1行足すだけで新しいツールが使えるようになった。モデルが正しいツールを選べたのは、ツールの説明文のおかげだと思う。似たツールが増えたとき、選び間違いは起きないのか気になった。
