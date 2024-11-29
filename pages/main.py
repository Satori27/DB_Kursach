import streamlit as st
import requests
from pages.bids import *
from pages.tenders import *
from pages.request import *

# Конфигурация API


def login_page():
    st.title("Авторизация и Регистрация")

    mode = st.radio("Выберите действие:", ("Авторизация", "Регистрация"))

    if mode=="Регистрация":
        username = st.text_input("Имя пользователя")
        first_name = st.text_input("Имя")
        last_name = st.text_input("Фамилия")
        password = st.text_input("Пароль", type="password")
    else:
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")


    # Обработка действий
    if st.button("Отправить"):
        if mode == "Регистрация":
            if username and password and first_name and last_name:
                data = {"username": username, "password": password, "first_name": first_name, "last_name": last_name}
                response = send_request("auth/register", data=data)
                
                if response.status_code == 200:
                    st.success("Регистрация прошла успешно!")
                else:
                    st.error(f"Ошибка регистрации: {response.json().get('message')}")
            else:
                st.error("Пожалуйста, заполните все поля!")
        
        elif mode == "Авторизация":
            if username and password:
                data = {"username": username, "password": password}
                response = send_request("auth/login", data=data)
                
                if response.status_code == 200:
                    # Сохранение cookie
                    cookies = response.cookies.get_dict()
                    st.success("Авторизация успешна!")
                    st.session_state["cookies"] = response.cookies.get_dict()
                    
                else:
                    st.error(f"Ошибка авторизации: {response.json().get('message', 'Неизвестная ошибка')}")
            else:
                st.error("Пожалуйста, заполните все поля!")






def home_page():
    if "cookies" in st.session_state:
        st.title("Вы успешно вошли в систему.")
    else:
        st.write("Войдите в систему")
        return
    

    st.subheader("Тендеры")
    if st.button("Создать тендер"):
        st.session_state["current_page"] = "create_tender_page"
    
    if st.button("Предложения на мои тендеры"):
        st.session_state["current_page"] = "bids_to_tenders"

    if st.button("Изменить мой тендер"):
        st.session_state["current_page"] = "change_my_tender"
    
    if st.button("Изменить версию моего тендера"):
        st.session_state["current_page"] = "change_tender_version"
    
    st.subheader("Предложения")
    if st.button("Создать предложение"):
        st.session_state["current_page"] = "create_bid_page"
    
    if st.button("Изменить моё предложение"):
        st.session_state["current_page"] = "change_my_bid"
    
    if st.button("Изменить версию моего предложения"):
        st.session_state["current_page"] = "change_bid_version"
    
    if st.button("Принятые мною предложения"):
        st.session_state["current_page"] = "approved_bids"

    if st.button("Предложения, которые у меня приняли"):
        st.session_state["current_page"] = "approved_bids"

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "create_tender_page"


    if st.session_state["current_page"] == "create_tender_page":
        st.title("Создать тендер:")
        create_tender_page()
    if st.session_state["current_page"]=="bids_to_tenders":
        st.title("Предложения на мои тендеры:")
        bids_to_tenders()
    if st.session_state["current_page"]=="change_my_tender":
        st.title("Изменить мой тендер:")
        change_tender_page()
    if st.session_state["current_page"]=="change_tender_version":
        st.title("Изменить версию моего тендера:")
        change_tender_version()
    if st.session_state["current_page"] == "create_bid_page":
        st.title("Создать предложение:")
        create_bid_page()
    if st.session_state["current_page"]=="change_my_bid":
        st.title("Изменить моё предложение:")
        change_bid_page()
    if st.session_state["current_page"]=="change_bid_version":
        st.title("Изменить версию моего предложения:")
        change_bid_version()
    if st.session_state["current_page"]=="approved_bids":
        st.title("Предложения которые я принял:")
        approved_bids()
        

def main():
    st.sidebar.title("Навигация")
    page = st.sidebar.radio(
        "Перейти к странице",
        ["login", "home"],
    )
    if page == "login":
        login_page()
    elif page == "home":
        home_page()
        pass

if __name__ == "__main__":
    main()