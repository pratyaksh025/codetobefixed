from connection import mycon
import bcrypt as b
import streamlit as st
import random as rd
from datetime import date
import re
import time


hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

#cursor
conn = mycon()
cur = conn.cursor(buffered=True)

#balance check
def balance_check():
    st.markdown("""
        <h1 style='text-align: center; color: red; font-family: "Georgia", serif; font-weight: 600;'>Balance Check</h1>
        """, unsafe_allow_html=True)
  
    st.image('sbi.png', width=800)
    
    s_acc = st.text_input("Enter Account Number:", key="s_acc")


    if s_acc:
        try:
            new_s_acc = int(s_acc)
            cur.execute("CALL new_select(%s)", (new_s_acc,))
            result = cur.fetchone()

            while cur.nextset():
                pass  

            if result:
                name = result[1]
                bal = result[5]
            else:
                name = "Unknown"
                bal = "N/A"
            
            if st.button("Check"):
                if result is None:
                    st.error("User Not Found")
                    time.sleep(2)
                    st.success("Below is your Registration form. We will be happy to have you.")
                    time.sleep(2)
                    st.session_state["show_create_user"] = True
                    st.rerun()
                else:
                    st.success("Processing...")
                    time.sleep(2)
                    st.success(f"Dear Customer, {name}, Your Account Balance is ₹{bal}")
        except Exception as e:
            while cur.nextset():
                pass  
            st.error(f"An error occurred: {e}")

#front page
def front_page():
    st.markdown("""
        <h1 style='text-align: center; color: blue; font-family: "Georgia", serif; font-weight: 600;'>SBI Bank</h1>
        <h3 style='text-align: center; color: aquamarine; font-family: "Georgia", serif; font-weight: 600;'>Welcome to SBI Bank</h3>
        """, unsafe_allow_html=True)

    st.image("sbi.png",width=800)
    
    if st.button("Navigate to Login Page"):
        login_page()

#transaction
def transaction():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in to perform a transaction.")
        login_page()
        return

    sender = st.text_input("Sender Account", key="sender")
    receiver = st.text_input("Receiver Account", key="receiver")
    amount = st.text_input("Enter Amount", key="trans_amount")

    if st.button("Pay"):
        try:
            amount = int(amount)  # Convert amount to integer

            # Start a transaction
            cur.execute("START TRANSACTION")

            # Fetch sender's balance
            cur.execute("SELECT balance FROM transaction WHERE account_number = %s", (sender,))
            result = cur.fetchone()

            if not result:
                st.error("Sender account not found.")
                cur.execute("ROLLBACK")
                return

            sender_balance = result[0]

            # Check for sufficient balance
            if amount > sender_balance:
                st.error("Insufficient balance.")
                cur.execute("ROLLBACK")
                return

            # Deduct amount from sender
            cur.execute("UPDATE transaction SET balance = balance - %s WHERE account_number = %s", (amount, sender))

            # Add amount to receiver
            cur.execute("UPDATE transaction SET balance = balance + %s WHERE account_number = %s", (amount, receiver))

            # Commit transaction
            cur.execute("COMMIT")
            st.success("Payment Successful!")

        except ValueError:
            st.error("Invalid amount. Please enter a numeric value.")
        except Exception as e:
            cur.execute("ROLLBACK")
            st.error(f"Transaction failed: {e}")


#create user
def create_user():
    st.title("Registration Form")
    st.image("reg.png", width=250)

    account_num = rd.randint(100000, 999999)
    entered_name = st.text_input("Name: ", key="name_input")
    contact_number = st.text_input("Primary Mobile: ", key="mobile_input")
    address = st.text_input("Address: ", key="address_input")
    email = st.text_input("Email:", key="email_input")
    password = st.text_input("Password:", type="password", key="password_input")
    amount = st.text_input("Provide your opening amount:", key="amount_input")
    selected_date = st.date_input("Select a Date", value=date.today(), key="date_input")

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    col1, col2, col3, col4 = st.columns([1, 1, 1, 4])
    with col4:
        if st.button("Create"):
            if not entered_name or not contact_number or not email or not password or not amount:
                st.error("All fields except Address are required!")
                return
            if not re.match(email_pattern, email):
                st.error("Invalid Email! Please enter a valid email address.")
                return
            try:
                amount = int(amount)
                if amount < 0:
                    st.error("Amount cannot be negative!")
                    return
            except ValueError:
                st.error("Please enter a valid numeric amount!")
                return
            try:
                query = "CALL create_client(%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (entered_name, contact_number, address, email, password, amount, selected_date, account_num)
                cur.execute(query, values)

                while cur.nextset():
                    pass

                conn.commit()
                st.success(f"Account successfully created! Username: {entered_name}, Account Number: {account_num}. Please take a screenshot for future reference.")
                time.sleep(25)
                st.session_state["show_create_user"] = False
                st.session_state["menu_selection"] = "Home-page"
                time.sleep(2)
                st.rerun()
            except Exception as e:
                while cur.nextset():
                    pass
                conn.rollback()
                st.error(f"An error occurred: {e}")

#login page
def login_page():
    st.session_state["login"] = False
    st.markdown("""
        <h1 style='text-align: center; color: blue; font-family: "Georgia", serif; font-weight: 600;'>SBI Bank Login</h1>
        """, unsafe_allow_html=True)
    user = st.text_input("Enter your username")
    pasw = st.text_input("Enter your password", type="password")
    
    if st.button("Login"):
        query = "SELECT pass FROM user WHERE username = %s"
        cur.execute(query, (user,))
        result = cur.fetchone()
        if result is None:
            st.error("User not found!")
            return
        if b.checkpw(pasw.encode(), result[0]):
            st.success("Login Successful!")
            st.session_state["login"] = True
            st.session_state["menu_selection"] = "Home-page"
            time.sleep(2)
            st.rerun()
        else:
            st.error("Invalid Password!")


#select menu
def select_menu():
    st.sidebar.title("Menu")
    menu = ["Home-page", "Transaction", "Balance", "Create User","login-Page"]
    choice = st.sidebar.selectbox("Selection", menu)
    return choice

#main page
def main_page():
    choice=select_menu()

    if choice==None or choice=="":
        front_page()
        st.info("Please select an option from the menu")

    if choice=="Home-page": 
        front_page()
        st.info("Please select an option from the menu")

    if choice=="Create User":
        create_user()
    
    if choice=="login-Page":
        login_page()

    if choice=="Transaction":
        transaction()

    if choice=="Balance":
        balance_check() 

main_page()

  
    
