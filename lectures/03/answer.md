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


## 宿題

### 取り組んだレベル
実装

### やったこと
- `app/tools.py` に `save_learning_log(entry)` を作成した。`learning_log/` が無ければ自動で作り、`learning_log.md` に日時の見出し付きで追記する。空の記録は保存せず、その旨を返す
- `app/agent.py` で `requires_approval=True` を付けて登録し、`output_type` を `[str, DeferredToolRequests]` にした
- CLI で、承認待ちが返っている間は「[承認待ち] ツール名(引数)」を表示して y/N を聞き、y または yes のときだけ承認にした。結果は `requests.build_results(approvals=...)` でまとめ、`message_history=result.all_messages()` と一緒に `run_sync` へ渡して再実行するようにした
- `save_learning_log` の docstring を「保存前の確認は、このツールに設定された承認機能が行う」に直した
- `INSTRUCTIONS` に「学習記録の保存を頼まれたら、文章で確認を求めず save_learning_log を呼び出す。承認後はツールの実行結果に基づいて回答し、再度承認を求めない」を追記した
- テスト `test_save_learning_log_appends_entry` を追加した。`uv run pytest -q` は 16 passed

### 結果
- `--list-tools`：`save_learning_log`（引数 `entry`）がモデルに見えるツールとして4個目に表示された
- 拒否（n）：
  - 質問：「今日の学習内容を記録して」
  - `[承認待ち] save_learning_log({'entry': '本日の学習を実施しました。'})` で止まり、n を入力
  - `[tool return] save_learning_log -> The tool call was denied.` と返り、モデルは「キャンセルされました」と利用者に伝えた
  - `ls learning_log` は「No such file or directory」で、何も保存されなかった
- 承認（y）：
  - 質問：「今日はLoRAとQLoRAの違いを学んだ。学習記録に保存して」
  - `[承認待ち] save_learning_log({'entry': '今日はLoRAとQLoRAの違いを学んだ。'})` で止まり、y を入力
  - `[tool return] save_learning_log -> 学習記録を …/learning_log/learning_log.md に保存しました。`
  - `cat learning_log/learning_log.md` で、日時の見出し（2026-11-07T12:39:29+00:00）の下に「今日はLoRAとQLoRAの違いを学んだ。」が保存されていた
- 記録内容を含まない依頼では、モデルが「何を記録しますか？」と聞き返し、ツールは呼ばれなかった（requests=1）

### 気づき・疑問
- 最初の docstring に「実行前に必ず利用者の承認を得る」と書いたところ、モデルは `save_learning_log` を呼ばず、文章で「保存してよいですか。『保存して』とお知らせください」と聞き返すだけだった（呼ばれたのは `search_glossary` の2回のみ）。これは `requires_approval=True` による承認ではなく、モデルが自分で確認した動きで、仕組みとしての承認が働いていなかった
- docstring を直し、`INSTRUCTIONS` にも追記すると、承認待ちで止まるようになった。ただし2か所を同時に変えたため、どちらが効いたのかは切り分けていない
- 承認の確認はモデルの文章ではなくプログラム側で行われる。取り消しにくい操作の安全策は、モデルへの指示だけに頼らず、仕組みで担保する方が確実だと分かった
- 承認して保存に成功した実行で、モデルの回答は「保存の完了には承認操作が必要」と事実と合わなかった。この実行は `INSTRUCTIONS` に追記する前だった可能性があり、追記後に再実行して改善したかは未確認（要確認）
- 同じ実行で、回答末尾が「関係する回：第7回」だった。LoRA・QLoRA は用語集では第2回で、この質問では `search_glossary` が呼ばれず、モデルが推測で答えたためと考えられる。INSTRUCTIONS の「回答の最後に関係する回を示す」は、検索せずに答えると誤りうる
- 疑問：承認後の回答が不正確になる原因は、承認結果の渡し方か、モデルの解釈か。コードを変えずに INSTRUCTIONS だけで改善できるかを、今後試したい
  
