
import streamlit as st
from datetime import date

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

# セッション内でタスクを管理
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "next_id" not in st.session_state:
    st.session_state.next_id = 0

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
                st.session_state.tasks.append({
                    "id": st.session_state.next_id,
                    "name": name.strip(),
                    "priority": priority,
                    "category": category,
                    "deadline": deadline,
                    "done": False
                })

                st.session_state.next_id += 1
                st.rerun()

# -----------------------------
# 2. 進捗状況
# -----------------------------
all_tasks = st.session_state.tasks

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
            task["deadline"],
            PRIORITY_ORDER[task["priority"]]
        )
    )

elif sort_by == "優先度が高い順":
    filtered.sort(
        key=lambda task: (
            task["done"],
            PRIORITY_ORDER[task["priority"]],
            task["deadline"]
        )
    )

else:
    filtered.sort(key=lambda task: task["id"])

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
                key=f"done_{task['id']}"
            )

            if done != task["done"]:
                task["done"] = done
                st.rerun()

        with middle:
            st.caption(
                f"優先度：{task['priority']} ｜ "
                f"カテゴリ：{task['category']} ｜ "
                f"期限：{task['deadline']:%Y-%m-%d}"
            )

            if (
                not task["done"]
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
                key=f"delete_{task['id']}"
            ):
                st.session_state.tasks = [
                    t for t in all_tasks
                    if t["id"] != task["id"]
                ]
                st.rerun()

st.divider()
st.caption(
    "※ タスクは現在のセッション内でのみ保持されます。"
    "セッション終了やサーバー再起動で消える場合があります。"
)