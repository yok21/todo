todoリストアプリ
PythonとStreamlitで開発した, タスク管理Webアプリケーションで.

優先度・期限・カテゴリによるタスク管理に加え, Supabaseを利用したユーザー認証とデータの永続化に対応しています.

アプリのURL : https://yok-todo.streamlit.app/

主な機能
1. ユーザー認証：メールアドレスによる新規登録・ログイン・ログアウト
2. タスク管理：タスクの追加・完了状態の変更・削除
3. 優先度設定：高・中・低の3段階
4. 期限管理：期限切れ・当日期限の通知
5. カテゴリ分類：大学・就活・アルバイト・プライベート・その他
6. 検索・絞り込み：キーワード・状態・優先度・カテゴリ
7. 並び替え：期限順・優先度順・追加順
8. 進捗表示：全タスク数・完了数・未完了数・完了率
9. データ保存：Supabase PostgreSQLによる永続化
10. アクセス制御：RLSによるユーザーごとのタスク管理

使用技術
開発言語：Python
Webフレームワーク：Streamlit
データベース：PostgreSQL(Supabase)
認証：Supabase Auth
アクセス制限：Row Level Security(RLS)
バージョン管理：Git/GitHub
デプロイ：Streamlit Community Cloud

開発者
GitHub: https://github.com/yok21
