        # =================================================
        # MAINTENANCE
        # =================================================

        elif owner_menu == "Maintenance":

            st.subheader(
                "🔧 Maintenance Management"
            )

            maintenance = get_data(
                "SELECT * FROM Maintenance"
            )

            st.dataframe(
                maintenance,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader(
                "🚗 Vehicles in Maintenance"
            )

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
                WHERE Status='Maintenance'
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

            st.subheader(
                "Add Maintenance Record"
            )

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
                    (
                        maintenance_vehicle_id,
                    )
                )

                st.success(
                    "Maintenance record added."
                )
