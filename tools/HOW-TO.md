# Hors Champ 画像の追加手順（Claude用）

ユーザーがChatGPTで作った映画紹介の画像5枚（縦4:5、文字なし）を映画名と一緒に送ってくる。
それを「カルーセル（文字入れ5枚）」と「リール（9:16、約25秒）」にして予約に入れる。

## 1. 文字入れ（カルーセル）
- spec.json を作る（tools/example-spec.json を参照）。
  - 1枚目：title に『映画名』＋つかみの一言
  - 2〜4枚目：あらすじ・見どころ（ネタバレなし、1行25字前後×2行）
  - 5枚目：title「こんな人に観てほしい」＋3行
  - y は文字を置く高さ（px、画像は1122x1402）。絵の余白に合わせる。絵に重なるときは "band": true
- `python3 tools/overlay.py spec.json` → out フォルダに 1〜5.jpg（サイン Hors Champ n/5 入り）
- 一覧画像を作って目で確認してから使う。

## 2. リール
- `python3 tools/reel.py spec.json <effect> out.mp4`
  - effect: petals（花びら）/ snow（雪）/ rain（雨）/ steam（湯気）/ digital（緑の光）/ dust（光の粒）。作品の空気に合うものを選ぶ。
  - 元画像（文字なし）を使い、文字は上部に入る。

## 3. アップロード
- `posts/<slug>/1〜5.jpg` と `reels/<slug>.mp4` に置いて push。
- URL: https://raw.githubusercontent.com/crazyayocrazy/horschamp-images/main/<パス>

## 4. 予約に追加
予約リスト https://claude.ai/artifact/4rS49ysni9N3MGCqKToRHz の db（ArtifactData ツール）
- collection "queue"（カルーセル、毎晩20:47投稿）: {film, order, date, status:"queued", image_urls[5], caption}
- collection "reels"（リール、毎日12:41投稿）: {film, order, date, status:"queued", video_url, caption}
- order は既存の最大+1。同じ作品はリールとカルーセルを同じ日にそろえる。
- キャプション：ネタバレなし3行＋ハッシュタグ10個前後（#映画紹介 #おすすめ映画 #水彩画 #HorsChamp など）。リールは短めに「詳しい紹介は今夜の投稿で。」

## 画像プロンプトを作るとき
各作品ブロックの2行目に必ず STYLE 行（white watercolor paper, ink lines, ONLY accent color = 指定色, NOT digital painting…）を入れる。
構図は後ろ姿で奥へ歩く・横一列の後ろ姿・半分余白を使わず、5枚すべてちがう構図に。結末の場面は描かない。
