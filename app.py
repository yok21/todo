import streamlit as st
from datetime import date
from supabase import create_client  # ★追加

st.set_page_config(
    page_title="My ToDo",
    page_icon="📝",
    layout="wide"
)

st.title("📝 My ToDo")
st.caption("優先度・期限・カテゴリでタスクを整理")

# 選択肢
CATEGORIES = [
    "大学", "就活", "アルバイト",
    "プライベート", "その他"
]
PRIORITIES = ["高", "中", "低"]
PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}

# -----------------------------
# ★追加：Supabase接続・ログイン
# -----------------------------
def create_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

def save_session(session):
    st.session_state.access_token = session.access_token
    st.session_state.refresh_token = session.refresh_token
    st.session_state.user_id = session.user.id

def clear_session():
    for key in ["access_token", "refresh_token", "user_id"]:
        st.session_state.pop(key, None)

supabase = create_supabase()

# 以前のセッションがあれば認証状態を復元
if "access_token" in st.session_state:
    try:
        response = supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        if response.session is None:
            raise ValueError("認証セッションがありません")

        save_session(response.session)

    except Exception:
        clear_session()
        st.warning("ログインの有効期限が切れました。")

# ログインしていない場合
if "user_id" not in st.session_state:

    login_tab, signup_tab = st.tabs([
        "ログイン", "新規登録"
    ])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("メールアドレス")
            password = st.text_input(
                "パスワード", type="password"
            )
            login = st.form_submit_button(
                "ログイン", type="primary"
            )

            if login:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email.strip(),
                        "password": password
                    })

                    if response.session is None:
                        st.error("ログインできませんでした。")
                    else:
                        save_session(response.session)
                        st.rerun()

                except Exception:
                    st.error(
                        "ログインに失敗しました。"
                        "メールアドレスとパスワードを確認してください。"
                    )

    with signup_tab:
        with st.form("signup_form"):
            new_email = st.text_input(
                "登録メールアドレス"
            )
            new_password = st.text_input(
                "登録パスワード",
                type="password"
            )
            signup = st.form_submit_button("新規登録")

            if signup:
                if not new_email.strip() or len(new_password) < 8:
                    st.warning(
                        "メールアドレスと8文字以上の"
                        "パスワードを入力してください。"
                    )
                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": new_email.strip(),
                            "password": new_password
                        })

                        if response.session:
                            save_session(response.session)
                            st.rerun()
                        else:
                            st.success(
                                "登録を受け付けました。"
                                "確認メールが届いた場合は、"
                                "メール内のリンクを開いてから"
                                "ログインしてください。"
                            )

                    except Exception as e:
                        st.error("登録に失敗しました。")
                        st.error(str(e))
    st.stop()

# ログアウト
with st.sidebar:
    st.success("ログイン中")

    if st.button("ログアウト"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        clear_session()
        st.rerun()

# -----------------------------
# ★追加：データベース操作
# -----------------------------
user_id = st.session_state.user_id

def load_tasks():
    response = (
        supabase.table("tasks")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )

    tasks = response.data

    # データベースの文字列をdate型に変換
    for task in tasks:
        if task["deadline"]:
            task["deadline"] = date.fromisoformat(
                task["deadline"]
            )

    return tasks

try:
    all_tasks = load_tasks()
except Exception:
    st.error(
        "タスクを取得できませんでした。"
        "Supabaseの接続とアクセス権限を確認してください。"
    )
    st.stop()

# -----------------------------
# 1. タスク追加
# -----------------------------
with st.expander("➕ 新しいタスクを追加", expanded=True):
    with st.form("add_task", clear_on_submit=True):
        name = st.text_input(
            "タスク名",
            placeholder="例：レポートを提出する"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            priority = st.selectbox(
                "優先度", PRIORITIES, index=1
            )

        with col2:
            category = st.selectbox(
                "カテゴリ", CATEGORIES
            )

        with col3:
            deadline = st.date_input(
                "期限", value=date.today()
            )

        submitted = st.form_submit_button(
            "タスクを追加", type="primary"
        )

        if submitted:
            if not name.strip():
                st.warning("タスク名を入力してください。")
            else:
                try:
                    # ★変更：Supabaseに保存
                    supabase.table("tasks").insert({
                        "user_id": user_id,
                        "name": name.strip(),
                        "priority": priority,
                        "category": category,
                        "deadline": deadline.isoformat(),
                        "done": False
                    }).execute()

                    st.rerun()

                except Exception:
                    st.error(
                        "タスクの追加に失敗しました。"
                        "接続や権限を確認してください。"
                    )

# -----------------------------
# 2. 進捗状況
# -----------------------------
completed = sum(task["done"] for task in all_tasks)
total = len(all_tasks)
remaining = total - completed
rate = completed / total if total else 0

st.subheader("📊 進捗状況")

c1, c2, c3, c4 = st.columns(4)

c1.metric("全タスク", total)
c2.metric("完了", completed)
c3.metric("未完了", remaining)
c4.metric("完了率", f"{rate:.0%}")

st.progress(rate)


# -----------------------------
# 3. 検索・絞り込み
# -----------------------------
st.subheader("🔍 検索・絞り込み")

search = st.text_input(
    "キーワード検索",
    placeholder="タスク名で検索"
)

f1, f2, f3, f4 = st.columns(4)

with f1:
    status_filter = st.selectbox(
        "状態", ["すべて", "未完了", "完了"]
    )

with f2:
    priority_filter = st.selectbox(
        "優先度", ["すべて"] + PRIORITIES
    )

with f3:
    category_filter = st.selectbox(
        "カテゴリ", ["すべて"] + CATEGORIES
    )

with f4:
    sort_by = st.selectbox(
        "並び順",
        [
            "期限が近い順",
            "優先度が高い順",
            "追加した順"
        ]
    )

filtered = [
    task for task in all_tasks
    if search.casefold() in task["name"].casefold()
    and (
        status_filter == "すべて"
        or task["done"] == (status_filter == "完了")
    )
    and (
        priority_filter == "すべて"
        or task["priority"] == priority_filter
    )
    and (
        category_filter == "すべて"
        or task["category"] == category_filter
    )
]

# 並び替え
if sort_by == "期限が近い順":
    filtered.sort(
        key=lambda task: (
            task["done"],
            task["deadline"] or date.max,
            PRIORITY_ORDER[task["priority"]]
        )
    )

elif sort_by == "優先度が高い順":
    filtered.sort(
        key=lambda task: (
            task["done"],
            PRIORITY_ORDER[task["priority"]],
            task["deadline"] or date.max
        )
    )

else:
    filtered.sort(
        key=lambda task: task["created_at"]
    )

# -----------------------------
# 4. タスク一覧
# -----------------------------
st.subheader(f"📋 タスク一覧（{len(filtered)}件）")

if not filtered:
    st.info("条件に一致するタスクがありません。")

for task in filtered:
    with st.container(border=True):
        left, middle, right = st.columns([5, 3, 1])

        with left:
            done = st.checkbox(
                task["name"],
                value=task["done"],
                key=f"done_{user_id}_{task['id']}"
            )

            if done != task["done"]:
                try:
                    # ★変更：Supabaseの完了状態を更新
                    (
                        supabase.table("tasks")
                        .update({"done": done})
                        .eq("id", task["id"])
                        .eq("user_id", user_id)
                        .execute()
                    )

                    st.rerun()

                except Exception:
                    st.error("完了状態の更新に失敗しました。")

        with middle:
            deadline_text = (
                task["deadline"].strftime("%Y-%m-%d")
                if task["deadline"] else "未設定"
            )

            st.caption(
                f"優先度：{task['priority']} ｜ "
                f"カテゴリ：{task['category']} ｜ "
                f"期限：{deadline_text}"
            )

            if (
                not task["done"]
                and task["deadline"] is not None
                and task["deadline"] < date.today()
            ):
                st.error("期限切れ")

            elif (
                not task["done"]
                and task["deadline"] == date.today()
            ):
                st.warning("今日が期限")

        with right:
            if st.button(
                "削除",
                key=f"delete_{user_id}_{task['id']}"
            ):
                try:
                    # ★変更：Supabaseから削除
                    (
                        supabase.table("tasks")
                        .delete()
                        .eq("id", task["id"])
                        .eq("user_id", user_id)
                        .execute()
                    )

                    st.rerun()

                except Exception:
                    st.error("タスクの削除に失敗しました.")

st.divider()
st.caption(
    "※ タスクはSupabaseに保存されます。"
    "ログアウト後も、再ログインすれば利用できます。"
)