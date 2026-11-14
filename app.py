import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
import os
from datetime import date

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Vehicle Rental System",
    page_icon="🚗",
    layout="wide"
)

# =========================================================
# DATABASE CONFIGURATION
# =========================================================

try:
    DB_CONFIG = {
        "host": st.secrets["mysql"]["host"],
        "user": st.secrets["mysql"]["user"],
        "password": st.secrets["mysql"]["password"],
        "database": st.secrets["mysql"]["database"]
    }
except Exception:
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "YOUR_MYSQL_PASSWORD"),
        "database": os.getenv("DB_NAME", "vehicle_rental_system")
    }

try:
    OWNER_REGISTRATION_KEY = st.secrets["owner"]["registration_key"]
except Exception:
    OWNER_REGISTRATION_KEY = os.getenv(
        "OWNER_REGISTRATION_KEY",
        "YOUR_OWNER_REGISTRATION_KEY"
    )

# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def run_query(query, values=(), fetch=False):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, values)

        if fetch:
            return cursor.fetchall()

        conn.commit()
        return True

    finally:
        cursor.close()
        conn.close()


def get_data(query, values=()):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(query, values)

        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        return pd.DataFrame(data, columns=columns)

    finally:
        cursor.close()
        conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def next_id(table, column):
    result = run_query(
        f"""
        SELECT COALESCE(MAX({column}), 0) + 1 AS next_id
        FROM {table}
        """,
        fetch=True
    )

    return result[0]["next_id"]


# =========================================================
# CREATE LOGIN TABLES
# =========================================================

def create_login_tables():

    run_query(
        """
        CREATE TABLE IF NOT EXISTS Customer_Login (
            Customer_ID INT PRIMARY KEY,
            Password VARCHAR(255) NOT NULL,
            FOREIGN KEY (Customer_ID)
            REFERENCES Customer(Customer_ID)
            ON DELETE CASCADE
        )
        """
    )

    run_query(
        """
        CREATE TABLE IF NOT EXISTS Owner_Login (
            Owner_ID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(100) NOT NULL,
            Email VARCHAR(100) UNIQUE NOT NULL,
            Password VARCHAR(255) NOT NULL
        )
        """
    )


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None


def logout():
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.user_id = None
    st.rerun()


# =========================================================
# DATABASE CONNECTION TEST
# =========================================================

try:
    create_login_tables()

except Exception as e:
    st.error("Unable to connect to MySQL database.")
    st.error(str(e))
    st.stop()


# =========================================================
# LOGIN / REGISTRATION PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <style>
        .main-title {
            text-align: center;
            font-size: 45px;
            font-weight: bold;
        }

        .sub-title {
            text-align: center;
            font-size: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-title">🚗 Vehicle Rental System</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Vehicle Rental Management Dashboard</div>',
        unsafe_allow_html=True
    )

    st.divider()

    login_tab, customer_tab, owner_tab = st.tabs(
        [
            "🔐 Login",
            "👤 Customer Registration",
            "👑 Owner Registration"
        ]
    )

    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader("🔐 Login")

        login_role = st.selectbox(
            "Login As",
            ["Customer", "Owner"],
            key="login_role"
        )

        if login_role == "Customer":
            login_id = st.text_input(
                "Customer ID",
                key="login_customer_id"
            )
        else:
            login_id = st.text_input(
                "Owner Email",
                key="login_owner_email"
            )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True,
            key="login_button"
        ):

            if not login_id or not login_password:
                st.warning("Please enter all details.")

            else:

                password = hash_password(login_password)

                if login_role == "Customer":

                    try:
                        result = run_query(
                            """
                            SELECT Customer_ID
                            FROM Customer_Login
                            WHERE Customer_ID=%s
                            AND Password=%s
                            """,
                            (login_id, password),
                            fetch=True
                        )

                        if result:
                            st.session_state.logged_in = True
                            st.session_state.role = "Customer"
                            st.session_state.user_id = int(login_id)
                            st.rerun()
                        else:
                            st.error(
                                "Invalid Customer ID or Password."
                            )

                    except Exception as e:
                        st.error(str(e))

                else:

                    try:
                        result = run_query(
                            """
                            SELECT Owner_ID
                            FROM Owner_Login
                            WHERE Email=%s
                            AND Password=%s
                            """,
                            (login_id, password),
                            fetch=True
                        )

                        if result:
                            st.session_state.logged_in = True
                            st.session_state.role = "Owner"
                            st.session_state.user_id = result[0]["Owner_ID"]
                            st.rerun()
                        else:
                            st.error(
                                "Invalid Owner Email or Password."
                            )

                    except Exception as e:
                        st.error(str(e))

    # =====================================================
    # CUSTOMER REGISTRATION
    # =====================================================

    with customer_tab:

        st.subheader("👤 Customer Registration")

        customer_name = st.text_input(
            "Full Name",
            key="customer_reg_name"
        )

        customer_phone = st.text_input(
            "Phone",
            key="customer_reg_phone"
        )

        customer_email = st.text_input(
            "Email",
            key="customer_reg_email"
        )

        customer_address = st.text_area(
            "Address",
            key="customer_reg_address"
        )

        customer_license = st.text_input(
            "License Number",
            key="customer_reg_license"
        )

        customer_password = st.text_input(
            "Create Password",
            type="password",
            key="customer_reg_password"
        )

        if st.button(
            "👤 Register as Customer",
            use_container_width=True,
            key="customer_register_button"
        ):

            if (
                not customer_name
                or not customer_phone
                or not customer_email
                or not customer_license
                or not customer_password
            ):
                st.warning("Please fill all required details.")

            else:

                try:
                    customer_id = next_id(
                        "Customer",
                        "Customer_ID"
                    )

                    run_query(
                        """
                        INSERT INTO Customer
                        (
                            Customer_ID,
                            Name,
                            Phone,
                            Email,
                            Address,
                            License_No
                        )
                        VALUES
                        (%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            customer_id,
                            customer_name,
                            customer_phone,
                            customer_email,
                            customer_address,
                            customer_license
                        )
                    )

                    run_query(
                        """
                        INSERT INTO Customer_Login
                        (
                            Customer_ID,
                            Password
                        )
                        VALUES
                        (%s,%s)
                        """,
                        (
                            customer_id,
                            hash_password(customer_password)
                        )
                    )

                    st.success(
                        f"Registration successful! "
                        f"Your Customer ID is {customer_id}"
                    )

                except Exception as e:
                    st.error(str(e))

    # =====================================================
    # OWNER REGISTRATION
    # =====================================================

    with owner_tab:

        st.subheader("👑 Owner Registration")

        owner_name = st.text_input(
            "Owner Name",
            key="owner_reg_name"
        )

        owner_email = st.text_input(
            "Owner Email",
            key="owner_reg_email"
        )

        owner_password = st.text_input(
            "Create Password",
            type="password",
            key="owner_reg_password"
        )

        owner_key = st.text_input(
            "Owner Registration Key",
            type="password",
            key="owner_reg_key"
        )

        if st.button(
            "👑 Register as Owner",
            use_container_width=True,
            key="owner_register_button"
        ):

            if not owner_name:
                st.warning("Please enter Owner Name.")

            elif not owner_email:
                st.warning("Please enter Owner Email.")

            elif not owner_password:
                st.warning("Please create a Password.")

            elif owner_key != OWNER_REGISTRATION_KEY:
                st.error("Invalid Owner Registration Key.")

            else:

                try:
                    run_query(
                        """
                        INSERT INTO Owner_Login
                        (
                            Name,
                            Email,
                            Password
                        )
                        VALUES
                        (%s,%s,%s)
                        """,
                        (
                            owner_name,
                            owner_email,
                            hash_password(owner_password)
                        )
                    )

                    st.success(
                        "Owner registration successful! "
                        "You can now login."
                    )

                except Exception as e:
                    st.error(str(e))


# =========================================================
# CUSTOMER AND OWNER DASHBOARDS
# =========================================================

else:

    # =====================================================
    # CUSTOMER PANEL
    # =====================================================

    if st.session_state.role == "Customer":

        st.sidebar.title("🚗 Customer Panel")

        customer_menu = st.sidebar.radio(
            "Menu",
            [
                "Dashboard",
                "Available Vehicles",
                "My Bookings"
            ],
            key="customer_menu"
        )

        if st.sidebar.button(
            "Logout",
            key="customer_logout"
        ):
            logout()

        customer_id = st.session_state.user_id

        customer = get_data(
            """
            SELECT *
            FROM Customer
            WHERE Customer_ID=%s
            """,
            (customer_id,)
        )

        if not customer.empty:
            customer_name = customer.iloc[0]["Name"]
        else:
            customer_name = "Customer"

        st.title(f"👋 Welcome, {customer_name}")

        # =================================================
        # CUSTOMER DASHBOARD
        # =================================================

        if customer_menu == "Dashboard":

            bookings = get_data(
                """
                SELECT *
                FROM Booking
                WHERE Customer_ID=%s
                """,
                (customer_id,)
            )

            vehicles = get_data(
                "SELECT * FROM Vehicle"
            )

            available = 0

            if not vehicles.empty:
                available = len(
                    vehicles[
                        vehicles["Status"] == "Available"
                    ]
                )

            total_spent = 0

            if not bookings.empty:
                total_spent = bookings["Total_Amount"].sum()

            c1, c2, c3 = st.columns(3)

            c1.metric("My Bookings", len(bookings))
            c2.metric("Available Vehicles", available)
            c3.metric("Total Spent", f"₹{total_spent:,.2f}")

        # =================================================
        # AVAILABLE VEHICLES
        # =================================================

        elif customer_menu == "Available Vehicles":

            st.subheader("🚘 Available Vehicles")

            vehicles = get_data(
                """
                SELECT *
                FROM Vehicle
                WHERE Status='Available'
                """
            )

            st.dataframe(
                vehicles,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("🚗 Book Vehicle")

            vehicle_id = st.number_input(
                "Vehicle ID",
                min_value=1,
                step=1,
                key="customer_booking_vehicle"
            )

            pickup_date = st.date_input(
                "Pickup Date",
                min_value=date.today(),
                key="customer_pickup_date"
            )

            return_date = st.date_input(
                "Return Date",
                min_value=pickup_date,
                key="customer_return_date"
            )

            if st.button(
                "🚗 Book Vehicle",
                use_container_width=True,
                key="customer_book_button"
            ):

                if return_date < pickup_date:
                    st.error(
                        "Return date cannot be before pickup date."
                    )

                else:

                    vehicle = get_data(
                        """
                        SELECT *
                        FROM Vehicle
                        WHERE Vehicle_ID=%s
                        AND Status='Available'
                        """,
                        (vehicle_id,)
                    )

                    if vehicle.empty:
                        st.error("Vehicle is not available.")

                    else:

                        days = (
                            return_date - pickup_date
                        ).days

                        days = max(days, 1)

                        rate = float(
                            vehicle.iloc[0]["Daily_Rate"]
                        )

                        total = rate * days

                        booking_id = next_id(
                            "Booking",
                            "Booking_ID"
                        )

                        run_query(
                            """
                            INSERT INTO Booking
                            (
                                Booking_ID,
                                Customer_ID,
                                Vehicle_ID,
                                Booking_Date,
                                Pickup_Date,
                                Return_Date,
                                Total_Amount
                            )
                            VALUES
                            (%s,%s,%s,%s,%s,%s,%s)
                            """,
                            (
                                booking_id,
                                customer_id,
                                vehicle_id,
                                date.today(),
                                pickup_date,
                                return_date,
                                total
                            )
                        )

                        run_query(
                            """
                            UPDATE Vehicle
                            SET Status='Rented'
                            WHERE Vehicle_ID=%s
                            """,
                            (vehicle_id,)
                        )

                        st.success(
                            f"Booking successful! "
                            f"Booking ID: {booking_id}"
                        )

        # =================================================
        # MY BOOKINGS
        # =================================================

        elif customer_menu == "My Bookings":

            st.subheader("📋 My Bookings")

            bookings = get_data(
                """
                SELECT
                    b.Booking_ID,
                    b.Booking_Date,
                    b.Pickup_Date,
                    b.Return_Date,
                    b.Total_Amount,
                    v.Vehicle_Number,
                    v.Brand,
                    v.Model
                FROM Booking b
                JOIN Vehicle v
                ON b.Vehicle_ID=v.Vehicle_ID
                WHERE b.Customer_ID=%s
                ORDER BY b.Booking_ID DESC
                """,
                (customer_id,)
            )

            st.dataframe(
                bookings,
                use_container_width=True,
                hide_index=True
            )

    # =====================================================
    # OWNER PANEL
    # =====================================================

    else:

        st.sidebar.title("👑 Owner Panel")

        owner_menu = st.sidebar.radio(
            "Management",
            [
                "Dashboard",
                "Customers",
                "Vehicles",
                "Bookings",
                "Payments",
                "Returns",
                "Maintenance",
                "Employees",
                "Branches",
                "Reports"
            ],
            key="owner_menu"
        )

        if st.sidebar.button(
            "Logout",
            key="owner_logout"
        ):
            logout()

        st.title("👑 Owner Dashboard")

        # =================================================
        # OWNER DASHBOARD
        # =================================================

        if owner_menu == "Dashboard":

            customers = get_data("SELECT * FROM Customer")
            vehicles = get_data("SELECT * FROM Vehicle")
            bookings = get_data("SELECT * FROM Booking")
            payments = get_data("SELECT * FROM Payment")
            maintenance = get_data("SELECT * FROM Maintenance")

            available = 0
            rented = 0

            if not vehicles.empty:

                available = len(
                    vehicles[
                        vehicles["Status"] == "Available"
                    ]
                )

                rented = len(
                    vehicles[
                        vehicles["Status"] == "Rented"
                    ]
                )

            revenue = 0

            if not bookings.empty:
                revenue = bookings["Total_Amount"].sum()

            maintenance_cost = 0

            if not maintenance.empty:
                maintenance_cost = maintenance["Cost"].sum()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total Customers", len(customers))
            c2.metric("Total Vehicles", len(vehicles))
            c3.metric("Available Vehicles", available)
            c4.metric("Total Bookings", len(bookings))

            c5, c6, c7 = st.columns(3)

            c5.metric("Rented Vehicles", rented)
            c6.metric("Total Revenue", f"₹{revenue:,.2f}")
            c7.metric("Maintenance Cost", f"₹{maintenance_cost:,.2f}")

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Vehicle Status")

                if not vehicles.empty:
                    st.bar_chart(
                        vehicles["Status"].value_counts()
                    )

            with col2:

                st.subheader("Vehicle Type")

                if not vehicles.empty:
                    st.bar_chart(
                        vehicles["Vehicle_Type"].value_counts()
                    )

        # =================================================
        # CUSTOMERS
        # =================================================

        elif owner_menu == "Customers":

            st.subheader("👤 Customer Management")

            customers = get_data("SELECT * FROM Customer")

            st.dataframe(
                customers,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Add Customer")

            name = st.text_input(
                "Customer Name",
                key="owner_customer_name"
            )

            phone = st.text_input(
                "Customer Phone",
                key="owner_customer_phone"
            )

            email = st.text_input(
                "Customer Email",
                key="owner_customer_email"
            )

            address = st.text_input(
                "Customer Address",
                key="owner_customer_address"
            )

            license_no = st.text_input(
                "License Number",
                key="owner_customer_license"
            )

            if st.button("Add Customer", key="owner_add_customer"):

                customer_id = next_id("Customer", "Customer_ID")

                run_query(
                    """
                    INSERT INTO Customer
                    VALUES
                    (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        customer_id,
                        name,
                        phone,
                        email,
                        address,
                        license_no
                    )
                )

                st.success(f"Customer added. ID: {customer_id}")

        # =================================================
        # VEHICLES
        # =================================================

        elif owner_menu == "Vehicles":

            st.subheader("🚘 Vehicle Management")

            vehicles = get_data("SELECT * FROM Vehicle")

            st.dataframe(
                vehicles,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Add Vehicle")

            vehicle_number = st.text_input(
                "Vehicle Number",
                key="vehicle_number"
            )

            brand = st.text_input("Brand", key="vehicle_brand")
            model = st.text_input("Model", key="vehicle_model")

            vehicle_type = st.selectbox(
                "Vehicle Type",
                ["Car", "SUV", "Bike", "Van", "Luxury"],
                key="vehicle_type"
            )

            daily_rate = st.number_input(
                "Daily Rate",
                min_value=0.0,
                step=100.0,
                key="vehicle_daily_rate"
            )

            status = st.selectbox(
                "Status",
                ["Available", "Rented", "Maintenance"],
                key="vehicle_status"
            )

            branch_id = st.number_input(
                "Branch ID",
                min_value=1,
                step=1,
                key="vehicle_branch_id"
            )

            if st.button("Add Vehicle", key="add_vehicle_button"):

                vehicle_id = next_id("Vehicle", "Vehicle_ID")

                run_query(
                    """
                    INSERT INTO Vehicle
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        vehicle_id,
                        vehicle_number,
                        brand,
                        model,
                        vehicle_type,
                        daily_rate,
                        status,
                        branch_id
                    )
                )

                st.success(f"Vehicle added. ID: {vehicle_id}")

        # =================================================
        # BOOKINGS
        # =================================================

        elif owner_menu == "Bookings":

            st.subheader("📅 Booking Management")

            bookings = get_data(
                """
                SELECT
                    b.Booking_ID,
                    c.Name AS Customer_Name,
                    v.Vehicle_Number,
                    b.Booking_Date,
                    b.Pickup_Date,
                    b.Return_Date,
                    b.Total_Amount
                FROM Booking b
                JOIN Customer c
                ON b.Customer_ID=c.Customer_ID
                JOIN Vehicle v
                ON b.Vehicle_ID=v.Vehicle_ID
                """
            )

            st.dataframe(
                bookings,
                use_container_width=True,
                hide_index=True
            )

        # =================================================
        # PAYMENTS
        # =================================================

        elif owner_menu == "Payments":

            st.subheader("💳 Payment Management")

            payments = get_data("SELECT * FROM Payment")

            st.dataframe(
                payments,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Add Payment")

            payment_id = st.number_input(
                "Payment ID",
                min_value=1,
                step=1,
                key="payment_id"
            )

            payment_booking_id = st.number_input(
                "Booking ID",
                min_value=1,
                step=1,
                key="payment_booking_id"
            )

            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                key="payment_amount"
            )

            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "UPI", "Card", "Net Banking"],
                key="payment_method"
            )

            payment_status = st.selectbox(
                "Payment Status",
                ["Paid", "Pending", "Failed"],
                key="payment_status"
            )

            transaction_id = st.text_input(
                "Transaction ID",
                key="payment_transaction_id"
            )

            if st.button("Add Payment", key="add_payment_button"):

                run_query(
                    """
                    INSERT INTO Payment
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        payment_id,
                        payment_booking_id,
                        date.today(),
                        amount,
                        payment_method,
                        payment_status,
                        transaction_id
                    )
                )

                st.success("Payment added successfully.")

        # =================================================
        # RETURNS
        # =================================================

        elif owner_menu == "Returns":

            st.subheader("🔄 Return Management")

            returns = get_data("SELECT * FROM `Return`")

            st.dataframe(
                returns,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Record Vehicle Return")

            return_id = st.number_input(
                "Return ID",
                min_value=1,
                step=1,
                key="return_id"
            )

            return_booking_id = st.number_input(
                "Booking ID",
                min_value=1,
                step=1,
                key="return_booking_id"
            )

            condition = st.text_input(
                "Vehicle Condition",
                key="return_condition"
            )

            late_fee = st.number_input(
                "Late Fee",
                min_value=0.0,
                step=100.0,
                key="return_late_fee"
            )

            remarks = st.text_area(
                "Remarks",
                key="return_remarks"
            )

            if st.button("Record Return", key="record_return_button"):

                run_query(
                    """
                    INSERT INTO `Return`
                    VALUES
                    (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        return_id,
                        return_booking_id,
                        date.today(),
                        condition,
                        late_fee,
                        remarks
                    )
                )

                booking = get_data(
                    """
                    SELECT Vehicle_ID
                    FROM Booking
                    WHERE Booking_ID=%s
                    """,
                    (return_booking_id,)
                )

                if not booking.empty:

                    run_query(
                        """
                        UPDATE Vehicle
                        SET Status='Available'
                        WHERE Vehicle_ID=%s
                        """,
                        (booking.iloc[0]["Vehicle_ID"],)
                    )

                st.success("Vehicle return recorded.")

        # =================================================
        # MAINTENANCE
        # =================================================

        elif owner_menu == "Maintenance":

            st.subheader("🔧 Maintenance Management")

            maintenance = get_data(
                "SELECT * FROM Maintenance"
            )

            st.dataframe(
                maintenance,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("🚗 Vehicles in Maintenance")

            maintenance_vehicles = get_data(
                """
                SELECT
                    Vehicle_ID,
                    Vehicle_Number,
                    Brand,
                    Model,
                    Vehicle_Type,
                    Status
                FROM Vehicle
                WHERE Status = 'Maintenance'
                """
            )

            st.metric(
                "Total Vehicles in Maintenance",
                len(maintenance_vehicles)
            )

            st.dataframe(
                maintenance_vehicles,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Add Maintenance Record")

            maintenance_id = st.number_input(
                "Maintenance ID",
                min_value=1,
                step=1,
                key="maintenance_id"
            )

            maintenance_vehicle_id = st.number_input(
                "Vehicle ID",
                min_value=1,
                step=1,
                key="maintenance_vehicle_id"
            )

            service_type = st.text_input(
                "Service Type",
                key="maintenance_service_type"
            )

            cost = st.number_input(
                "Cost",
                min_value=0.0,
                step=100.0,
                key="maintenance_cost"
            )

            description = st.text_area(
                "Description",
                key="maintenance_description"
            )

            if st.button(
                "Add Maintenance",
                key="add_maintenance_button"
            ):

                run_query(
                    """
                    INSERT INTO Maintenance
                    VALUES
                    (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        maintenance_id,
                        maintenance_vehicle_id,
                        date.today(),
                        service_type,
                        cost,
                        description
                    )
                )

                run_query(
                    """
                    UPDATE Vehicle
                    SET Status='Maintenance'
                    WHERE Vehicle_ID=%s
                    """,
                    (maintenance_vehicle_id,)
                )

                st.success("Maintenance record added.")

        # =================================================
        # EMPLOYEES
        # =================================================

        elif owner_menu == "Employees":

            st.subheader("👨‍💼 Employee Management")

            employees = get_data("SELECT * FROM Employee")

            st.dataframe(
                employees,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            employee_name = st.text_input(
                "Employee Name",
                key="employee_name"
            )

            employee_phone = st.text_input(
                "Employee Phone",
                key="employee_phone"
            )

            employee_email = st.text_input(
                "Employee Email",
                key="employee_email"
            )

            employee_role = st.text_input(
                "Role",
                key="employee_role"
            )

            employee_branch = st.number_input(
                "Branch ID",
                min_value=1,
                step=1,
                key="employee_branch"
            )

            if st.button("Add Employee", key="add_employee_button"):

                employee_id = next_id("Employee", "Employee_ID")

                run_query(
                    """
                    INSERT INTO Employee
                    VALUES
                    (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        employee_id,
                        employee_name,
                        employee_phone,
                        employee_email,
                        employee_role,
                        employee_branch
                    )
                )

                st.success(f"Employee added. ID: {employee_id}")

        # =================================================
        # BRANCHES
        # =================================================

        elif owner_menu == "Branches":

            st.subheader("🏢 Branch Management")

            branches = get_data("SELECT * FROM Branch")

            st.dataframe(
                branches,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            branch_name = st.text_input(
                "Branch Name",
                key="branch_name"
            )

            location = st.text_input(
                "Location",
                key="branch_location"
            )

            branch_phone = st.text_input(
                "Phone",
                key="branch_phone"
            )

            manager_name = st.text_input(
                "Manager Name",
                key="branch_manager"
            )

            if st.button("Add Branch", key="add_branch_button"):

                branch_id = next_id("Branch", "Branch_ID")

                run_query(
                    """
                    INSERT INTO Branch
                    VALUES
                    (%s,%s,%s,%s,%s)
                    """,
                    (
                        branch_id,
                        branch_name,
                        location,
                        branch_phone,
                        manager_name
                    )
                )

                st.success(f"Branch added. ID: {branch_id}")

        # =================================================
        # REPORTS
        # =================================================

        elif owner_menu == "Reports":

            st.subheader("📊 Reports")

            st.write("### 👤 Customer Booking Report")

            customer_report = get_data(
                """
                SELECT
                    c.Customer_ID,
                    c.Name,
                    COUNT(b.Booking_ID) AS Total_Bookings,
                    COALESCE(SUM(b.Total_Amount), 0) AS Total_Spending
                FROM Customer c
                LEFT JOIN Booking b
                ON c.Customer_ID=b.Customer_ID
                GROUP BY
                    c.Customer_ID,
                    c.Name
                ORDER BY Total_Spending DESC
                """
            )

            st.dataframe(
                customer_report,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.write("### 🚘 Vehicle Report")

            vehicle_report = get_data(
                """
                SELECT
                    v.Vehicle_ID,
                    v.Vehicle_Number,
                    v.Brand,
                    v.Model,
                    v.Status,
                    COUNT(b.Booking_ID) AS Total_Bookings
                FROM Vehicle v
                LEFT JOIN Booking b
                ON v.Vehicle_ID=b.Vehicle_ID
                GROUP BY
                    v.Vehicle_ID,
                    v.Vehicle_Number,
                    v.Brand,
                    v.Model,
                    v.Status
                """
            )

            st.dataframe(
                vehicle_report,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.write("### 💳 Payment Report")

            payment_report = get_data(
                """
                SELECT
                    Payment_Method,
                    Payment_Status,
                    COUNT(*) AS Transactions,
                    SUM(Amount) AS Total_Amount
                FROM Payment
                GROUP BY
                    Payment_Method,
                    Payment_Status
                """
            )

            st.dataframe(
                payment_report,
                use_container_width=True,
                hide_index=True
            )
