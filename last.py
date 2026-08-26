import random
import streamlit as st

st.set_page_config(page_title="ระบบจองเรือไปเกาะสมุย")


if "users" not in st.session_state:
    st.session_state["users"] = {"user": "1234"}
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "temp_booking" not in st.session_state:
    st.session_state["temp_booking"] = {}

if "available_seats" not in st.session_state:
    st.session_state["available_seats"] = {
        "08:00 น. - ซีทราน เฟอร์รี่ (170 บาท)": 15,
        "10:30 น. - ราชา เฟอร์รี่ (170 บาท)": 8,
        "13:30 น. - ซีทราน เฟอร์รี่ (170 บาท)": 20,
        "16:00 น. - สปีดโบ๊ท VIP (450 บาท)": 3,
    }

if st.session_state["page"] == "login":
    st.title(" เข้าสู่ระบบ")
    st.caption("ระบบจองเรือไปเกาะสมุย (ม.4/07)")

    u = st.text_input("ชื่อผู้ใช้งาน (Username)")
    p = st.text_input("รหัสผ่าน (Password)", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("เข้าสู่ระบบ", type="primary", use_container_width=True):
            if (
                u in st.session_state["users"]
                and st.session_state["users"][u] == p
            ):
                st.session_state["page"] = "booking"
                st.rerun()
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!")
    with col2:
        if st.button("สมัครสมาชิกใหม่", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()


elif st.session_state["page"] == "register":
    st.title("สมัครสมาชิกใหม่")
    reg_u = st.text_input("ตั้งชื่อผู้ใช้งาน (Username)")
    reg_p = st.text_input("ตั้งรหัสผ่าน (Password)", type="password")

    if st.button("ยืนยันลงทะเบียน", type="primary", use_container_width=True):
        if not reg_u or not reg_p:
            st.warning(" กรุณากรอกข้อมูลให้ครบทุกช่อง!")
        elif reg_u in st.session_state["users"]:
            st.warning(" ชื่อผู้ใช้งานนี้ถูกใช้ไปแล้ว!")
        else:
            st.session_state["users"][reg_u] = reg_p
            st.success("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
            st.session_state["page"] = "login"
            st.rerun()

    if st.button("กลับไปหน้าเข้าสู่ระบบ", use_container_width=True):
        st.session_state["page"] = "login"
        st.rerun()


elif st.session_state["page"] == "booking":
    st.title("เลือกรายการจองเรือ")

    route = st.selectbox(
        "1. เลือกเส้นทาง", ["ดอนสัก -> เกาะสมุย", "เกาะสมุย -> ดอนสัก"]
    )

    schedules = list(st.session_state["available_seats"].keys())
    schedule = st.selectbox("2. เลือกรอบเรือ", schedules)

  
    remaining = st.session_state["available_seats"][schedule]

  
    if remaining > 0:
        st.info(f"**ที่นั่งคงเหลือ:** {remaining} ที่นั่ง")
    else:
        st.error("❌ รอบเรือนี้ที่นั่งเต็มแล้ว (0 ที่นั่งเหลือ)")

    name = st.text_input("3. ชื่อ-นามสกุล ผู้โดยสาร")
    phone = st.text_input("4. เบอร์โทรศัพท์ (10 หลัก)")

  
    max_bookable = max(1, remaining)
    qty = st.number_input(
        "5. จำนวนที่นั่งที่ต้องการจอง (ที่)",
        min_value=1,
        max_value=max_bookable,
        value=1,
        disabled=(remaining == 0),
    )

    if st.button(
        "➡️ ตรวจสอบข้อมูลและชำระเงิน",
        type="primary",
        use_container_width=True,
        disabled=(remaining == 0),
    ):
        if not name or not phone:
            st.error("❌ กรุณากรอกชื่อ-นามสกุล และเบอร์โทรศัพท์ให้ครบถ้วน!")
        elif not phone.isdigit() or len(phone) != 10:
            st.error("❌ กรุณากรอกเบอร์โทรศัพท์เป็นตัวเลข 10 หลักให้ถูกต้อง!")
        elif qty > remaining:
            st.error(f"❌ จำนวนที่นั่งที่เลือกเกินจำนวนคงเหลือ ({remaining} ที่)!")
        else:
            price = 450 if "สปีดโบ๊ท" in schedule else 170
            st.session_state["temp_booking"] = {
                "name": name,
                "phone": phone,
                "route": route,
                "schedule": schedule,
                "qty": qty,
                "total": price * qty,
                "status": "รอการชำระเงิน (Pending)",
            }
            st.session_state["page"] = "payment"
            st.rerun()

    if st.button("ออกจากระบบ"):
        st.session_state["page"] = "login"
        st.rerun()


elif st.session_state["page"] == "payment":
    st.title("ตรวจสอบข้อมูล & ชำระเงิน")

    b = st.session_state["temp_booking"]

    st.subheader("1. สรุปความถูกต้องของข้อมูล")
    st.info(f"""
    * **ผู้โดยสาร:** {b['name']} ({b['phone']})
    * **เส้นทาง:** {b['route']}
    * **รอบเรือ:** {b['schedule']}
    * **จำนวนที่นั่งที่จอง:** {b['qty']} ที่นั่ง
    * **ยอดรวมสุทธิ:** {b['total']:,} บาท
    """)

    method = st.selectbox(
        "2. เลือกวิธีชำระเงิน",
        [
            "สแกน QR Code (PromptPay)",
            "โมบายแบงก์กิ้ง (Mobile Banking)",
            "บัตรเครดิต / เดบิต",
        ],
    )

    st.warning(f"**สถานะการชำระเงิน:** {b['status']}")

    if st.button(
        "ยืนยันการชำระเงิน & ออกตั๋ว",
        type="primary",
        use_container_width=True,
    ):
    
        sched_name = b["schedule"]
        st.session_state["available_seats"][sched_name] -= b["qty"]

        booking_code = f"SM{random.randint(100000, 900000)}"
        st.balloons()
        st.success("การจองและชำระเงินเสร็จสมบูรณ์!")

        with st.expander("ตั๋วโดยสาร / ใบยืนยันการจอง", expanded=True):
            st.write(f"**รหัสการจอง:** `{booking_code}`")
            st.write(f"**ชื่อผู้โดยสาร:** {b['name']}")
            st.write(f"**เส้นทาง:** {b['route']}")
            st.write(f"**รอบเรือ:** {b['schedule']}")
            st.write(f"**จำนวนที่นั่ง:** {b['qty']} ที่นั่ง")
            st.write(f"**ยอดชำระ:** {b['total']:,} บาท ({method})")
            st.write("**สถานะการจอง:** ยืนยันสำเร็จ (Confirmed)")

    if st.button(" ย้อนกลับไปแก้ไขข้อมูล"):
        st.session_state["page"] = "booking"
        st.rerun()