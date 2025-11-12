import streamlit as st
from database import (
    create_tables,
    add_user,
    verify_user,
    add_prescription,
    add_prescription_image,
    get_prescriptions,
    encrypt_prescription,
    encrypt_image,
    generate_key,
    decrypt_image,
)

create_tables()

def switch_page(page):
    st.session_state["page"] = page

def main():
    
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None
    if "encryption_key" not in st.session_state:
        st.session_state["encryption_key"] = generate_key()

    
    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "dashboard":
        dashboard_page()  


def login_page():
    st.title("CareCrypt  💊 : Your Secure Prescription Management System")
    
    choice = st.sidebar.selectbox("Select an Option", ["Login", "Sign Up"])

    if choice == "Sign Up":
       
        st.subheader("Create New Account")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Sign Up"):
            if email and password:
                if verify_user(email, password):
                    st.error("User already exists. Please log in.")
                else:
                    add_user(email, password)
                    st.success("Account created successfully. Please log in.")
            else:
                st.warning("Please enter both email and password.")

    elif choice == "Login":
        
        st.subheader("Login")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Log In"):
            if verify_user(email, password):
                st.session_state["user_email"] = email  # Store the user's email in session state
                st.success(f"Welcome back, {email}!")
                
                st.session_state["page"] = "dashboard"
                st.experimental_rerun()

            else:
                st.error("Invalid email or password. Please try again.")

def dashboard_page():
    st.title("Dashboard 📑- Secure Prescription Management System")
    st.sidebar.write(f"Logged in as: {st.session_state['user_email']}")
    st.sidebar.button("Logout", on_click=lambda: switch_page("login"))

    st.subheader("Upload and Encrypt Prescription")
    prescription_text = st.text_area("Enter Prescription Text")
    prescription_image = st.file_uploader("Upload Prescription Image", type=["png", "jpg", "jpeg"])

    if st.button("Encrypt and Save"):
        if not prescription_text and not prescription_image:
            st.warning("Please provide either a prescription text or an image.")
        else:
            encryption_key = st.session_state["encryption_key"]

        
            if prescription_text:
                encrypted_text = encrypt_prescription(prescription_text, encryption_key)
                add_prescription(1, prescription_text, encrypted_text.decode())  
                st.success("Text prescription encrypted and saved successfully.")

            
            if prescription_image:
                encrypted_image = encrypt_image(prescription_image.read(), encryption_key)
                add_prescription_image(1, encrypted_image)  
                st.success("Image prescription encrypted and saved successfully.")

    
    st.subheader("Your Prescriptions")
    prescriptions = get_prescriptions(1)  

    if prescriptions:
        for idx, (original, encrypted, encrypted_img, created_at) in enumerate(prescriptions, start=1):
            st.write(f"**Prescription #{idx}**")
            st.write(f"Original Text: {original}")
            st.write(f"Encrypted Text: {encrypted}")

            if encrypted_img:
                decrypted_img = decrypt_image(encrypted_img, st.session_state["encryption_key"])
                st.image(decrypted_img, caption="Decrypted Prescription Image", use_column_width=True)

            st.write(f"Created At: {created_at}")
            st.write("---")
    else:
        st.info("No prescriptions found.")


if __name__ == "__main__":
    main()
