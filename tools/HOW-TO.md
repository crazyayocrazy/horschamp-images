# Hors Champ 画像の追加手順（Claude用）

1. ユーザーがChatGPTで作った5枚（4:5）を受け取る。
2. spec.json を作る（example-spec.json を参照。1枚目＝タイトル＋つかみ、2〜4枚目＝あらすじ・見どころ、5枚目＝こんな人に観てほしい。ネタバレなし）。
3. `python3 tools/overlay.py spec.json` で文字とサイン（Hors Champ n/5）入りの 1〜5.jpg を作る。
4. `posts/YYYY-MM-DD-slug/` に置いて push。画像URLは
   https://raw.githubusercontent.com/crazyayocrazy/horschamp-images/main/posts/<フォルダ>/<n>.jpg
5. 予約リスト https://claude.ai/artifact/4rS49ysni9N3MGCqKToRHz の db collection "queue" に
   {film, order, date, status:"queued", image_urls, caption} を追加（order は既存の最大+1）。
6. 毎晩20:47に自動投稿タスクが queued の一番小さい order を投稿する。
