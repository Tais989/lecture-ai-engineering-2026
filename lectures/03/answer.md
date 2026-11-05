# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
- `--trace` で見えたツール呼び出し（ツール名と引数）：
- 1つの質問での LLM 呼び出し回数（`requests`）：
- 追加したツールと、docstring に書いた説明：

## 宿題

- 取り組んだレベル：基礎 / 実装 / 発展
- やったこと：
- 結果：
- 気づき・疑問：


## 演習

### 1. 第1回（素のLLM）とエージェントの回答の違い
質問：「AIE2026の講座の宿題にある「3レベル」とは何ですか？」

- 第1回（app.ask）：【第1回で得た回答を要約。講座のことを知らず「分からない」か一般論だったか】
- 第3回（app.agent）：用語集を検索してから答えた。「基礎・実装・発展の3段階で、いずれか1つに取り組めば完了」と答え、最後に「関連する回：第1回」を示した。
- 違い：エージェントは用語集（data/glossary.json）の内容に基づいて答え、最後に関係する回まで示した。【glossary.json の homework-levels と合っているか確認した結果】

### 2. --trace で見えたツール呼び出し
質問：「LoRAとQLoRAの違いは？」
- search_glossary({'query': 'LoRA'})
- search_glossary({'query': 'QLoRA'})
- 2つの用語を別々に検索していた。これは、INSTRUCTIONS の「答える前に必ず search_glossary で確認する」と、docstring の「query には調べたい用語を1つだけ入れる」に沿った動き。

### 3. 1つの質問でのLLM呼び出し回数（requests）
- 「LoRAとQLoRAの違いは？」：requests=2、tool_calls=2
- 「第2回の内容から確認問題を1問出して」：requests=2、tool_calls=1
- ツールを呼ぶ質問では、「LLM → ツール → LLM」のループにより、LLM が最低2回呼ばれた。

### 4. 追加したツールと docstring
- 追加したツール：make_quiz（app/tools.py に追加し、app/agent.py で登録）
- docstring：「用語集の用語から確認問題を1問作る。『確認問題を出して』と頼まれたときに使う。lecture が指定された場合はその回の用語から、指定がない場合は用語集全体から1つ選ぶ。問題と答えを返すので、利用者にはまず問題だけを出す。」
- 確認結果：
  - --list-tools で make_quiz と docstring が表示された
  - --trace で make_quiz({'lecture': 2}) が呼ばれ、「「量子化」の意味は何ですか？」と出題された
  - uv run pytest -q は 14 passed