import streamlit as st
from cryptography.fernet import Fernet
from database import (
    create_connection,
    add_prescription,
    add_prescription_image,
    get_prescriptions,
    generate_key,
    encrypt_prescription,
    decrypt_image,
)

def dashboard_page():
    
    email = st.session_state.get("user_email", None)

    if not email:
        st.error("You are not logged in!")
        return

    st.title("Dashboard 📑 - Secure Prescription Management System")
    st.write(f"Welcome to your dashboard, **{email}**!")

    
    if "encryption_key" not in st.session_state:
        st.session_state["encryption_key"] = generate_key()
    encryption_key = st.session_state["encryption_key"]

    
    st.subheader("Encrypt and Store Text Prescription")
    prescription_text = st.text_area("Enter Prescription Details", placeholder="Type your prescription here...")

    if st.button("Save Text Prescription"):
        if prescription_text:
            encrypted_text = encrypt_prescription(prescription_text, encryption_key)

            
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_id = c.fetchone()[0]

            
            add_prescription(user_id, prescription_text, encrypted_text.decode())
            st.success("Text prescription encrypted and saved successfully!")
        else:
            st.warning("Please enter the prescription details before saving.")

    
    st.subheader("Encrypt and Store Image Prescription")
    uploaded_image = st.file_uploader("Upload Prescription Image", type=["jpg", "jpeg", "png"])

    if st.button("Save Image Prescription"):
        if uploaded_image:
            image_data = uploaded_image.read()
            encrypted_image = Fernet(encryption_key).encrypt(image_data)

            
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_id = c.fetchone()[0]

            
            add_prescription_image(user_id, encrypted_image)
            st.success("Image prescription encrypted and saved successfully!")
        else:
            st.warning("Please upload an image before saving.")

    
    st.subheader("View My Prescriptions")
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    user_id = c.fetchone()[0]

    prescriptions = get_prescriptions(user_id)

    if prescriptions:
        for idx, (original, encrypted, encrypted_img, created_at) in enumerate(prescriptions, start=1):
            st.write(f"### Prescription #{idx}")
            if original:
                st.write(f"**Original Text Prescription:** {original}")
            if encrypted:
                st.write(f"**Encrypted Text Prescription:** {encrypted}")
            if encrypted_img:
                decrypted_img = decrypt_image(encrypted_img, encryption_key)
                st.image(decrypted_img, caption="Decrypted Prescription Image", use_column_width=True)
            st.write(f"**Created At:** {created_at}")
            st.write("---")
    else:
        st.info("No prescriptions found in your account.")

    
    if st.button("Log Out"):
        st.session_state["page"] = "login"
        st.session_state["user_email"] = None
        st.experimental_rerun()
