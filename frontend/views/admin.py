"""管理后台 page — CRUD operations for houses (admin only)."""

import pandas as pd
import streamlit as st

import api_client as api


def render() -> None:
    st.markdown("## 管理后台")
    st.caption("房源数据管理（增删改查）")

    tab1, tab2 = st.tabs(["房源列表", "新增 / 导入"])

    # ---- Tab 1: List & Edit ----
    with tab1:
        st.subheader("房源列表")

        search = st.text_input("搜索楼盘名称", key="admin_search")
        page = st.number_input("页码", 1, 100, 1, key="admin_page")

        params = {"page": page, "page_size": 20}
        if search:
            params["search"] = search

        resp = api.get_houses(params)
        items = resp.get("items", [])
        total = resp.get("total", 0)
        total_pages = resp.get("total_pages", 1)

        st.caption(f"共 {total} 条，第 {page}/{total_pages} 页")

        if items:
            df = pd.DataFrame(items)
            cols_to_show = ["id", "name", "place", "price", "property_type", "avg_area"]
            cols_to_show = [c for c in cols_to_show if c in df.columns]
            st.dataframe(df[cols_to_show].fillna("—"), use_container_width=True)

            st.subheader("编辑或删除")
            house_id = st.number_input("输入要编辑/删除的房源 ID", min_value=1, step=1, key="admin_edit_id")

            col_edit, col_del, _ = st.columns([1, 1, 3])

            with col_edit:
                if st.button("加载房源信息"):
                    house = api.get_house(house_id)
                    if house:
                        st.session_state["edit_house"] = house
                    else:
                        st.error("未找到该房源")

            with col_del:
                if st.button("删除房源", type="secondary"):
                    result = api.delete_house(house_id)
                    if result:
                        st.success("删除成功")
                        st.cache_data.clear()
                        st.rerun()

            # Edit form
            house = st.session_state.get("edit_house")
            if house:
                with st.form("edit_house_form"):
                    st.markdown(f"**编辑房源 #{house['id']}**")
                    new_name = st.text_input("名称", value=house.get("name", ""))
                    new_place = st.text_input("区域", value=house.get("place", ""))
                    new_price = st.number_input("价格 (元/㎡)", value=float(house.get("price", 0)), step=1000.0)
                    new_type = st.selectbox(
                        "房产类型",
                        ["住宅", "别墅", "商业"],
                        index=["住宅", "别墅", "商业"].index(house.get("property_type", "住宅")),
                    )
                    new_intro = st.text_area("介绍", value=house.get("introduction", "") or "")
                    new_room = st.number_input("户型（室）", value=int(house.get("room_count") or 0), step=1)
                    new_area = st.number_input("平均面积 (㎡)", value=float(house.get("avg_area") or 0), step=1.0)

                    if st.form_submit_button("更新房源"):
                        data = {
                            "name": new_name, "place": new_place, "price": new_price,
                            "property_type": new_type, "introduction": new_intro,
                            "room_count": new_room, "avg_area": new_area,
                        }
                        result = api.update_house(house["id"], data)
                        if result:
                            st.success("更新成功")
                            st.session_state.pop("edit_house", None)
                            st.rerun()

    # ---- Tab 2: Create & Import ----
    with tab2:
        st.subheader("新增房源")
        with st.form("create_house_form"):
            name = st.text_input("名称", key="create_name")
            place = st.text_input("区域", key="create_place")
            price = st.number_input("价格 (元/㎡)", min_value=0.0, step=1000.0, key="create_price")
            property_type = st.selectbox("房产类型", ["住宅", "别墅", "商业"], key="create_type")
            introduction = st.text_area("介绍", key="create_intro")
            col1, col2, col3 = st.columns(3)
            with col1:
                room_count = st.number_input("户型（室）", min_value=0, step=1, key="create_room")
            with col2:
                avg_area = st.number_input("平均面积 (㎡)", min_value=0.0, step=1.0, key="create_area")
            with col3:
                price_flag = st.text_input("价格标识", value="正常", key="create_flag")

            if st.form_submit_button("创建房源"):
                if not name or not place or price <= 0:
                    st.error("请填写名称、区域和有效的价格")
                else:
                    data = {
                        "name": name, "place": place, "price": price,
                        "property_type": property_type, "introduction": introduction,
                        "room_count": room_count, "avg_area": avg_area,
                        "price_flag": price_flag, "min_area": None, "max_area": None,
                    }
                    result = api.create_house(data)
                    if result:
                        st.success(f"创建成功！ID: {result.get('id')}")
                        st.rerun()

        st.markdown("---")
        st.subheader("批量导入 CSV")
        uploaded_file = st.file_uploader("选择 CSV 文件", type=["csv"], key="admin_csv")
        if uploaded_file and st.button("导入"):
            result = api.import_csv(uploaded_file.read(), uploaded_file.name)
            if result:
                st.success(f"导入完成：{result.get('imported', 0)} 条成功，{result.get('skipped', 0)} 条跳过")
                if result.get("errors"):
                    st.warning("\n".join(result["errors"][:10]))
