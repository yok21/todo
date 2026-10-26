import streamlit as st

# ページ設定
st.set_page_config(
    page_title="ToDoアプリ",
    page_icon="📝"
)

st.title("📝 ToDoリスト")
st.write("PythonとStreamlitで作成したアプリ")

# タスクを保存するリスト
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# タスク追加
with st.form("task_form", clear_on_submit=True):
    new_task = st.text_input("新しいタスク")

    submitted = st.form_submit_button("追加")

    if submitted and new_task.strip():
        st.session_state.tasks.append({
            "id": st.session_state.get("next_id", 0),
            "name": new_task.strip(),
            "done": False
        })
        st.session_state.next_id = (
            st.session_state.get("next_id", 0) + 1
        )
        st.rerun()

st.divider()

# タスク一覧
st.subheader("タスク一覧")

tasks = st.session_state.tasks

if not tasks:
    st.info("タスクがありません")

for task in tasks:
    col1, col2 = st.columns([5, 1])

    with col1:
        task["done"] = st.checkbox(
            task["name"],
            value=task["done"],
            key=f"task_{task['id']}"
        )

    with col2:
        if st.button(
            "削除",
            key=f"delete_{task['id']}"
        ):
            st.session_state.tasks = [
                t for t in tasks
                if t["id"] != task["id"]
            ]
            st.rerun()

# 未完了タスク数
remaining = sum(
    not task["done"]
    for task in st.session_state.tasks
)

st.metric("未完了タスク", remaining)