import streamlit as st
from pages.request import send_request

def create_tender_page():
    data = dict()
    data["name"] = st.text_input("Имя тендера")
    data["description"] = st.text_input("описание тендера")
    cookies = st.session_state["cookies"]

    if st.button("Отправить"):
        if data["name"] and data["description"]:
            resp = send_request("/tenders/new", "POST", data=data, cookies=cookies)
            if resp.status_code==200:
                st.success("Тендер успешно создан")
            else:
                st.error(f"Ошибка: {resp.json().get('message')}")
        else:
            st.error("Заполните все поля")


def change_tender_page():
    cookies = st.session_state["cookies"]
    resp = send_request("/tenders/my", "GET", cookies=cookies)
    if resp.status_code==200:
        if resp.json()==[]:
            st.write("У вас нету тендеров")
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

            st.subheader("Изменить тендер")
            changed_name  = st.text_input("Изменить имя тендера")
            changed_description  = st.text_input("Изменить описание тендера")
            changed_status = st.selectbox("Изменить статус", ["Created", "Published", "Closed"])

            if st.button("Отправить"):
                if (changed_name or changed_description or changed_status):
                    data = dict()
                    data["name"] = changed_name
                    data["description"] = changed_description
                    data["status"] = changed_status
                    response_patch = send_request(f"/tenders/{tender_id}/edit", "PATCH", data=data, cookies=cookies)
                    if response_patch.status_code==200:
                        st.success("Тендер успешно изменен")
                    else:
                        st.error(f"Ошибка: {response_patch.json().get('message')}")
                else:
                    st.error("Заполните одно из полей")

     


def change_tender_version():
    cookies = st.session_state["cookies"]
    resp = send_request("/tenders/my", "GET", cookies=cookies)
    if resp.status_code==200:
        if resp.json()==[]:
            st.write("У вас нету тендеров")
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

            st.subheader("Изменить  версию тендера")
            response_version = send_request(f"tenders/{tender_id}/versions", "GET", cookies=cookies)
            selected_object_versions = st.selectbox(
                "Выберите тендер для просмотра информации",
                response_version.json(),
                format_func=lambda obj:  obj["version"] 
            )

            if selected_object:
                version_name = selected_object_versions["name"]
                version_description = selected_object_versions["description"]
                version_status = selected_object_versions["status"]
                version_version = selected_object_versions["version"]
                version_created_at = selected_object_versions["created_at"]
                version_tender_id = selected_object_versions["id"]
                st.subheader(f"Информация об тендере \"{version_name}\"")
                st.write(f"Описание тендера: {version_description}")
                st.write(f"Статус: {version_status}")
                st.write(f"Версия: {version_version}")
                st.write(f"Когда создан {version_created_at}")
                
                if st.button("Изменить на эту версию"):
                    response_patch_version = send_request(f"/tenders/{tender_id}/rollback/{version_version}/", "PUT", cookies=cookies)
                    if response_patch_version.status_code==200:
                        st.success("Тендер успешно изменен")
                    else:
                        st.error(f"Ошибка: {response_patch_version.json().get('message')}")



def bids_to_tenders():
    cookies = st.session_state["cookies"]
    response = send_request("/tenders/my/bids", method="GET", cookies=cookies)
    if response.status_code==200:
        if response.json()==[]:
            st.write("У вас нету предложений на ваши тендеры")
            return

        selected_object = st.selectbox(
            "Выберите тендер для просмотра информации",
            response.json(),
            format_func=lambda obj:  obj["name"] 
        )
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

            st.subheader(f"Предложения на тендер \"{name}\"")

            response_bids = send_request(f"bids/{tender_id}", method="GET", cookies=cookies)
            if response_bids.json()==[]:
                st.write("У вас нету предложений на ваши тендеры")
                return
            selected_object_bid = st.selectbox(
                "Выберите тендер для просмотра информации",
                response_bids.json(),
                format_func=lambda obj:  obj["name"] 
            )
            if selected_object_bid:
                bid_name = selected_object_bid["name"]
                bid_description = selected_object_bid["description"]
                bid_status = selected_object_bid["status"]
                bid_version = selected_object_bid["version"]
                bid_created_at = selected_object_bid["created_at"]
                bid_id = selected_object_bid["id"]

                st.write(f"Имя предложения: {bid_name}")
                st.write(f"Описание предложения: {bid_description}")
                st.write(f"Статус: {bid_status}")
                st.write(f"Версия: {bid_version}")
                st.write(f"Когда создан {bid_created_at}")

                approve_btn = st.button("Approve")
                reject_btn = st.button("Reject")

                if approve_btn:
                    response = send_request(f"/bids/{bid_id}/edit", method="PATCH", cookies=cookies, data={"status": "Approved"})
                    if response.status_code==200:
                        st.success("Предложение принято")
                elif reject_btn:
                    response = send_request(f"/bids/{bid_id}/edit", method="PATCH", cookies=cookies, data={"status": "Rejected"})
                    if response.status_code==200:
                        st.success("Предложение отклонено")
