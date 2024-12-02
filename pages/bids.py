import streamlit as st

from pages.request import send_request

def create_bid_page():
    cookies = st.session_state["cookies"]
    resp = send_request("/tenders/", "GET", cookies=cookies)
    if resp.status_code==200:
        if resp.json()==[]:
            st.write("Пока нет опубликованных тендеров")
            return

        selected_object = st.selectbox(
            "Выберите тендер для просмотра информации",
            resp.json(),
            format_func=lambda obj:  obj["name"] 
        )

        # Показываем информацию о выбранном объекте
        if selected_object:
            name = selected_object["name"]
            description = selected_object["description"]
            status = selected_object["status"]
            version = selected_object["version"]
            created_at = selected_object["created_at"]
            tender_id = selected_object["id"]
            st.subheader(f"Информация об тендере \"{name}\"")
            st.write(f"Описание тендера: {description}")
            st.write(f"Статус: {status}")
            st.write(f"Версия: {version}")
            st.write(f"Когда создан {created_at}")

            st.subheader("Создать предложение на этот тендер")
            bid_name  = st.text_input("имя предложения")
            bid_description  = st.text_input("Описание предложения")

            if st.button("Отправить"):
                if (bid_name and bid_description):
                    data = dict()
                    data["name"] = bid_name
                    data["description"] = bid_description
                    data["tenderId"] = tender_id
                    response_patch = send_request("/bids/new", "POST", data=data, cookies=cookies)
                    if response_patch.status_code==200:
                        st.success("Предложение успешно создано")
                    else:
                        st.error(f"Ошибка: {response_patch.json().get('message')}")
                else:
                    st.error("Заполните все поля")



def change_bid_page():
    cookies = st.session_state["cookies"]
    resp = send_request("/bids/my/", "GET", cookies=cookies)
    if resp.status_code==200:
        if resp.json()==[]:
            st.write("У вас нету предложений")
            return

        selected_object = st.selectbox(
            "Выберите предложение для просмотра информации",
            resp.json(),
            format_func=lambda obj:  obj["name"] 
        )

        # Показываем информацию о выбранном объекте
        if selected_object:
            name = selected_object["name"]
            description = selected_object["description"]
            status = selected_object["status"]
            version = selected_object["version"]
            created_at = selected_object["created_at"]
            bidId = selected_object["id"]
            st.subheader(f"Информация об предложении \"{name}\"")
            st.write(f"Описание предложения: {description}")
            st.write(f"Статус: {status}")
            st.write(f"Версия: {version}")
            st.write(f"Когда создан {created_at}")

            st.subheader("Изменить предложение")
            changed_name  = st.text_input("Изменить имя предложения")
            changed_description  = st.text_input("Изменить описание предложения")
            changed_status = st.selectbox("Изменить статус", ["Created", "Published", "Closed"])

            if st.button("Отправить"):
                if (changed_name or changed_description or changed_status):
                    data = dict()
                    data["name"] = changed_name
                    data["description"] = changed_description
                    data["status"] = changed_status
                    response_patch = send_request(f"/bids/{bidId}/edit", "PATCH", data=data, cookies=cookies)
                    if response_patch.status_code==200:
                        st.success("Предложение успешно изменено")
                    else:
                        st.error(f"Ошибка: {response_patch.json().get('message')}")
                else:
                    st.error("Заполните одно из полей")




def change_bid_version():
    cookies = st.session_state["cookies"]
    resp = send_request("/bids/my/", "GET", cookies=cookies)
    if resp.status_code==200:
        if resp.json()==[]:
            st.write("У вас нету предложений")
            return

        selected_object = st.selectbox(
            "Выберите предложение для просмотра информации",
            resp.json(),
            format_func=lambda obj:  obj["name"] 
        )

        # Показываем информацию о выбранном объекте
        if selected_object:
            name = selected_object["name"]
            description = selected_object["description"]
            status = selected_object["status"]
            version = selected_object["version"]
            created_at = selected_object["created_at"]
            bid_id = selected_object["id"]
            st.subheader(f"Информация о предложении \"{name}\"")
            st.write(f"Описание предложения: {description}")
            st.write(f"Статус: {status}")
            st.write(f"Версия: {version}")
            st.write(f"Когда создан {created_at}")

            st.subheader("Изменить  версию предложения")
            response_version = send_request(f"bids/{bid_id}/versions", "GET", cookies=cookies)
            selected_object_versions = st.selectbox(
                "Выберите предложение для просмотра информации",
                response_version.json(),
                format_func=lambda obj:  obj["version"] 
            )

            if selected_object:
                version_name = selected_object_versions["name"]
                version_description = selected_object_versions["description"]
                version_status = selected_object_versions["status"]
                version_version = selected_object_versions["version"]
                version_created_at = selected_object_versions["created_at"]
                version_bid_id = selected_object_versions["id"]
                st.subheader(f"Информация об предложении \"{version_name}\"")
                st.write(f"Описание предложения: {version_description}")
                st.write(f"Статус: {version_status}")
                st.write(f"Версия: {version_version}")
                st.write(f"Когда создан {version_created_at}")
                
                if st.button("Изменить на эту версию"):
                    response_patch_version = send_request(f"/bids/{bid_id}/rollback/{version_version}/", "PUT", cookies=cookies)
                    if response_patch_version.status_code==200:
                        st.success("Предложение успешно изменено")
                    else:
                        st.error(f"Ошибка: {response_patch_version.json().get('message')}")

def approved_bids():
    cookies = st.session_state["cookies"]
    resp = send_request("/bids/approved/", "GET", cookies=cookies)
    if resp.status_code==200:
        if resp.json()==[]:
            st.write("У вас нету активных предложений")
            return
        
        for js in resp.json():

            name = js["tender_name"]
            description = js["tender_description"]
            status = js["tender_status"]

            st.subheader(f"Имя тендера: {name}")
            st.write(f"Описание тендера: {description}")
            st.write(f"Статус: {status}")

            bid_name = js["bid_name"]
            bid_description = js["bid_description"]
            bid_status = js["bid_status"]
            st.text("\n")
            st.write(f"Имя предложения: \"{bid_name}\"")
            st.write(f"Описание предложения: {bid_description}")
            st.write(f"Статус: {bid_status}")



