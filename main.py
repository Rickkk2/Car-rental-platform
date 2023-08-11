import datetime
from unicodedata import category
from jinja2 import Undefined
import streamlit as st
import pandas as pd
from aux_func import *
import time


# ----------------------- LAYOUT ---------------------------
st.set_page_config(page_title="Alquiler de Coches")


# ----------------------- BACKEND ---------------------------
oficinas_df = pd.read_csv('oficinas_db.csv', index_col=0)
car_df = pd.read_csv('car_db.csv', index_col=0)
reservas_df = pd.read_csv('reservas_db.csv', index_col=0)
descuentos_df = pd.read_csv('descuentos_db.csv')

# ----------------------- Navigation ---------------------------
# Comprobamos si el usuario es administrador
is_admin = is_admin(st.session_state.get('user_id'))
if is_admin:
    page_list = ("Alquilar Coche", "Modificar datos de usuario","Mis reservas" ,"Gestionar oficinas","Gestionar coches","Comprobar facturación")
else:
    page_list = ("Alquilar Coche", "Modificar datos de usuario","Mis reservas")
page = navigation(st, page_list)


    
# ----------------------- Multipage ---------------------------

# INICIO DE SESIÓN
if page == "Inicio de Sesión":
    placeholder = st.empty()

    with placeholder.container():
        st.header("Iniciar sesión")

        # Introducir datos
        usuario = st.text_input('Email o usuario')
        contraseña = st.text_input('Contraseña', type='password')

        # Botón de inicio de sesión
        if st.button('Iniciar sesión'):
            user_id = check_user_and_password(usuario, contraseña)
            if user_id == -1:
                st.error("Usuario o contraseña incorrectos")
            else:
                st.session_state['page'] = "Alquilar Coche"
                st.session_state['user_id'] = user_id
                st.success("Sesión iniciada correctamente. Ya puedes comenzar a alquilar un coche.")
                st.experimental_rerun()
        
        st.write("\n")
        st.write("\n")
        st.write("\n")


        st.subheader("¿No tienes cuenta?")
        # Botón de registro
        if st.button('Ir a registro'):
            st.session_state['page'] = "Registro usuario"
            st.experimental_rerun()

# REGISTRO DE USUARIO
elif page == "Registro usuario":
    placeholder = st.empty()

    with placeholder.container():
        st.header("Registrar usuario")

        email = st.text_input('Introduce tu email')
        usuario = st.text_input('Introduce tu usuario')
        contraseña = st.text_input('Contraseña', type='password')
        contraseña2 = st.text_input('Repite la contraseña', type='password')
        admin = st.checkbox('Soy administrador')
        code = "0"
        if admin:
            code = st.text_input('Introduce el código de administrador')
            
              
        if st.button('Registrar usuario'):
            if check_register_data(st,email, usuario, contraseña, contraseña2,admin,code):
                # Añadir en la base de datos
                state, user_id = add_user(usuario, contraseña, email, admin)

                if state == 0:
                    st.success("Registro completado correctamente. Ya puedes comenzar a alquilar un coche.")
                    time.sleep(2)
                    st.session_state['user_id'] = user_id
                    st.session_state['page'] = "Alquilar Coche"
                    st.experimental_rerun()
                else:
                    st.error("Error al registrar usuario.")

        st.subheader("¿Ya tienes cuenta?")
        # Botón de registro
        if st.button('Ir a inicio de sesión'):
            st.session_state['page'] = "Iniciar sesión"
            st.experimental_rerun()

# MODIFICAR DATOS DE USUARIO
elif page == "Modificar datos de usuario":
    placeholder = st.empty()

    with placeholder.container():
        st.header("Modificar mis datos")

        old_email, old_usuario, old_contraseña = get_user_data(st.session_state['user_id'])

        email = st.text_input('Nuevo Email', old_email)
        usuario = st.text_input('Nuevo Usuario', old_usuario)
        contraseña = st.text_input('Nueva Contraseña', type='password')
        contraseña2 = st.text_input('Contraseña antigua', type='password')
              
        if st.button('Realizar cambios'):
            # Comprobamos que la contraseña el válida
            user_id = check_user_and_password(old_usuario, contraseña=contraseña2)
            if user_id == -1:
                st.error("Contraseña incorrecta")

            # Comprobamos que la información es válida
            elif check_register_data(st,email, usuario, contraseña, contraseña,False,"",drop=st.session_state['user_id']):
                # Cambiar en la base de datos
                state = edit_user(st,usuario, contraseña, email, st.session_state['user_id'])

                if state == 0:
                    st.success("Cambios completados con éxito.")

                else:
                    st.error("Error al cambiar datos de usuario.")
        
        st.write("\n")
        
        if st.button('Eliminar cuenta'):
                state = delete_user(st.session_state['user_id'])
                if state == 0:
                    time.sleep(2)
                    st.success("Cuenta eliminada correctamente.")
                    st.session_state.clear()
                    st.experimental_rerun()
                else:
                    st.error("Error al eliminar cuenta.")

# GESTIÓN DE OFICINAS
elif page == "Gestionar oficinas":
    placeholder = st.empty()

    with placeholder.container():
        st.title("Gestión de oficinas")

        # Mostrar oficinas
        st.subheader("Oficinas")
        st.write(oficinas_df)

        # Añadir oficinas
        st.subheader("Añadir oficina")
        nombre = st.text_input('Nombre de la oficina')

        # Botón de añadir oficina
        if st.button('Añadir oficina'):
            state = add_office(nombre)
            if state == 0:
                st.success("Oficina añadida correctamente.")
                st.experimental_rerun()
            elif state == 1:
                st.error("Ya existe una oficina con ese nombre.")
            else:
                st.error("Error al añadir oficina.")

        # Eliminar oficina
        st.subheader("Eliminar oficina")
        oficina = st.selectbox('Selecciona la oficina a eliminar', oficinas_df['Nombre'])

        office_index = oficinas_df[oficinas_df['Nombre'] == oficina].index[0]

        # Botón de eliminar oficina
        if st.button('Eliminar oficina'):
            state = delete_office(office_index)
            if state == 0:
                st.success("Oficina eliminada correctamente.")
                st.experimental_rerun()
            else:
                st.error("Error al eliminar oficina.")

        # Modificar oficina
        st.subheader("Modificar oficina")
        oficina = st.selectbox('Selecciona la oficina a modificar', oficinas_df["Nombre"])
        nombre = st.text_input('Nuevo nombre de la oficina')
        
        office_index = oficinas_df[oficinas_df['Nombre'] == oficina].index[0]

        # Botón de modificar oficina
        if st.button('Modificar oficina'):
            state = edit_office(office_index, nombre)
            if state == 0:
                st.success("Oficina modificada correctamente.")
                st.experimental_rerun()
            elif state == 1:
                st.error("Ya existe una oficina con ese nombre.")
            else:
                st.error("Error al modificar oficina.")

# GESTIÓN DE COCHES
elif page == "Gestionar coches":
    placeholder = st.empty()

    with placeholder.container():
        st.title("Gestión de vehículos")

        # Mostrar vehículo
        st.subheader("Vehículos")
        st.write(car_df)

        # Añadir vehículos
        st.subheader("Añadir vehículo")
        nombre = st.text_input('Nombre del vehículo')
        marca = st.text_input('Marca del vehículo')
        modelo = st.text_input('Modelo del vehículo')
        category = st.selectbox('Categoría del vehículo', ['Gama baja', 'Gama media', 'Gama alta'])        
        manual = True if st.selectbox('Tipo de vehículo', ['Manual', 'Automatico']) == 'Manual' else False
        num_puertas = st.selectbox('Número de puertas', [2, 3, 4, 5, 6, 7, 8])
        solar_roof = True if st.selectbox('Techo solar', ['Sí', 'No']) == 'Sí' else False
        oficina = st.selectbox('Oficina', oficinas_df['Nombre'])
        precio_dia = st.number_input('Precio por día', min_value=0., value=0.,step=1.,format="%.2f")
        
        # Botón de añadir vehículo
        if st.button('Añadir vehículo'):
            state = add_car(nombre,marca,modelo,category,manual,num_puertas,solar_roof,oficina,precio_dia)
            if state == 0:
                st.success("Vehículo añadido correctamente.")
                time.sleep(2)
                st.experimental_rerun()
            elif state == 1:
                st.error("Ya existe un vehículo con ese nombre.")
            else:
                st.error("Error al añadir vehículo.")

        # Eliminar vehículo
        st.subheader("Eliminar vehículo")
        car = st.selectbox('Selecciona el vehículo a eliminar', car_df['Name'])

        car_index = car_df[car_df['Name'] == car].index[0]

        # Botón de eliminar vehículo
        if st.button('Eliminar oficina'):
            state = delete_car(car_index)
            if state == 0:
                st.success("Vehículo eliminado correctamente.")
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error("Error al eliminar vehículo.")

        # Modificar vehículo
        st.subheader("Modificar vehículo")
        car = st.selectbox('Selecciona el vehículo a modificar', car_df["Name"], index=0)
        car_index = car_df[car_df['Name'] == car].index[0]
        nombre = st.text_input('Nuevo nombre del vehículo', car_df.loc[car_index, 'Name'])
        marca = st.text_input('Nueva marca del vehículo', car_df.loc[car_index, 'Marca'])
        modelo = st.text_input('Nuevo modelo del vehículo', car_df.loc[car_index, 'Modelo'])
        category = st.selectbox('Nueva categoría del vehículo', ['Gama baja', 'Gama media', 'Gama alta'])
        manual = True if st.selectbox('Nueva transmisión del vehículo', ['Manual', 'Automatico']) == 'Manual' else False
        num_puertas = st.selectbox('Nuevo número de puertas', [2, 3, 4, 5, 6, 7, 8])
        solar_roof = True if st.selectbox('Nuevo techo solar', ['Sí', 'No']) == 'Sí' else False
        oficina = st.selectbox('Nueva oficina', oficinas_df['Nombre'])
        precio_dia = st.number_input('Nuevo precio por día',value=float(car_df.loc[car_index, 'Precio_por_dia']), min_value=0.,step=1.,format="%.2f")
        


        # Botón de modificar vehículo
        if st.button('Modificar vehículo'):
            state = edit_car(car_index, nombre, marca, modelo, category, manual, num_puertas, solar_roof, oficina, precio_dia)
            if state == 0:
                st.success("Vehículo modificado correctamente.")
                time.sleep(1)
                st.experimental_rerun()
            elif state == 1:
                st.error("Ya existe un vehículo con ese nombre.")
            else:
                st.error("Error al modificar vehículo.")



elif page == "Mis reservas":
    placeholder = st.empty()

    with placeholder.container():
        st.title("Mis reservas")

        st.header("Gestionar reservas")

        client_ID = st.session_state.get('user_id')
        booking_ids = get_user_bookings(client_ID)
        reservas = reservas_df.loc[booking_ids]
        
        # if reservas undefined 
        if reservas.empty:
            st.write("No tienes reservas")
        else:
            st.dataframe(reservas.drop(['Tipo Cliente','Num_Tarjeta','Titular'], axis = 1))

        # Eliminar vehículo
        st.subheader("Eliminar reserva")
        reserva_index = st.selectbox('Selecciona la reserva a eliminar', reservas.index)


        # Botón de eliminar vehículo
        if st.button('Eliminar reserva'):
            state = delete_user_booking(client_ID,reserva_index)
            if state == 0:
                st.success("Reserva eliminada correctamente.")
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error("Error al eliminar reserva.")

# COMPROBAR FACTURAS
elif page == "Comprobar facturación":
    placeholder = st.empty()

    with placeholder.container():
        st.title("Comprobar facturación")

        st.header("Consulta la facturación para un periodo")

        # current day datetime
        today = datetime.datetime.now()

        # start_time = st.date_input("Fecha de inicio",datetime.date(2019, 7, 6))
        # end_time = st.date_input("Fecha de fin",datetime.date(2021, 7, 6))

        start_time = st.date_input("Fecha de inicio",datetime.date(2020, 1, 1))
        end_time = st.date_input("Fecha de fin",datetime.date(today.year, today.month, today.day))

        
        if st.button('Comprobar facturación'):
            # Get all bookings for the period
            bookings = get_bookings_for_period(start_time, end_time)
            facturación = 0
            if bookings is None:
                st.error("No hay reservas para ese periodo.")
                
            else:
                facturación = bookings["Cantidad Pago"].sum() # Total amount paid

            st.header(f"Total facturado: {facturación}€")
            

        



elif page == "Alquilar Coche":
    placeholder = st.empty()
    with placeholder.container():
        st.title("Alquiler de Coches")
        st.header("Reservar coche")
        st.subheader("Datos de recogida")
        # Seleccionar oficina recogida
        oficina_recogida = st.selectbox("Elegir oficina de recogida", oficinas_df['Nombre'].tolist())

        cols = st.columns(2)
        # Seleccionar fecha y hora recogida
        fecha_recogida = cols[0].date_input("Fecha de recogida", datetime.date.today(), min_value=datetime.date.today())
        hora_recogida = cols[1].time_input("Hora de recogida", datetime.time(hour=8, minute=0))

        st.subheader("Datos de entrega")
        # Seleccionar oficina entrega
        oficina_entrega = st.selectbox("Elegir oficina de entrega", oficinas_df['Nombre'].tolist())

        cols = st.columns(2)
        # Seleccionar fecha y hora entrega
        fecha_entrega = cols[0].date_input("Fecha de entrega", fecha_recogida, min_value=fecha_recogida)
        hora_entrega = cols[1].time_input("Hora de entrega", datetime.time(hour=8, minute=0))

        check_datetime_value = check_datetime(fecha_recogida, hora_recogida, fecha_entrega, hora_entrega)
        
        if check_datetime_value == 1:
            st.error("Hora de recogida no válida. El horario de apertura es de 8:00 a 22:00")
        elif check_datetime_value == 2:
            st.error("Hora de entrega no válida. El horario de apertura es de 8:00 a 22:00")
        elif check_datetime_value == 3:
            st.error("Hora de recogida mayor o igual a la hora de entrega. ")
        elif check_datetime_value == 4:
            st.error("Fecha de recogida posterior a fecha de entrega.")
        elif check_datetime_value == 5:
            st.error("Hora de recogida anterior a fecha actual.")
        else:
            st.subheader("Elegir vehículo")
            car_df = get_available_cars(oficina_recogida)

            # Reservar vehículo
            car_gamma_selected = st.selectbox("Seleccionar gama", car_df['Category'].unique())
            cols = st.columns(2)
            car_brand_selected = cols[0].selectbox("Seleccionar coche", car_df[car_df["Category"] == car_gamma_selected]['Marca'].unique())
            available_cars = car_df[(car_df["Marca"] == car_brand_selected) & (car_df["Category"] == car_gamma_selected)]['Modelo']
            car_model_selected = cols[1].selectbox("Seleccionar modelo", available_cars.unique())
            available_cars = car_df[(car_df["Category"] == car_gamma_selected) & (car_df['Marca'] == car_brand_selected) & (car_df['Modelo'] == car_model_selected)]
            conducción_selected = st.radio("Conducción", available_cars["Manual"].map({False:"Automático", True:"Manual"}).unique())
            conduccion_binary = 1 if conducción_selected == "Manual" else 0
            available_cars = car_df[(car_df["Category"] == car_gamma_selected) & (car_df['Marca'] == car_brand_selected) & (car_df['Modelo'] == car_model_selected) & (car_df['Manual'] == conduccion_binary)]
            num_puertas_selected = st.radio("Número de puertas", available_cars["Num_Puertas"].unique())
            available_cars = car_df[(car_df["Category"] == car_gamma_selected) & (car_df['Marca'] == car_brand_selected) & (car_df['Modelo'] == car_model_selected) & (car_df['Manual'] == conduccion_binary) & (car_df['Num_Puertas'] == num_puertas_selected)]
            solar_roof_selected = st.radio("Techo Solar", available_cars["Solar_Roof"].map({False:"No", True:"Si"}).unique())
            soalr_roof_binary = 1 if solar_roof_selected == "Si" else 0
            available_cars = car_df[(car_df["Category"] == car_gamma_selected) & (car_df['Marca'] == car_brand_selected) & (car_df['Modelo'] == car_model_selected) & (car_df['Manual'] == conduccion_binary) & (car_df['Num_Puertas'] == num_puertas_selected) & (car_df['Solar_Roof'] == soalr_roof_binary)]
            lista_coches_disponibles = available_cars["Name"].to_list()
            lista_coches_disponibles.insert(0,"Ninguno")
            car_selected = st.selectbox("Seleccionar coche", lista_coches_disponibles)
            
            if car_selected != "Ninguno":

                #Obtener el precio por tarifa
                coche_elegido = available_cars.loc[available_cars['Name'] == str(car_selected)]
                precio_base = coche_elegido['Precio_por_dia'].to_list()[0]
                precio_tarifa = 0

                #Seleccionar tarifa 
                st.subheader("Tarifas")
                tarifa = st.radio("Seleccione el tipo de tarifa que desea aplicar",('Por kilometraje', 'Por día', 'Semanal', 'De fin de semana','De larga duración'))

                num_dias=(fecha_entrega-fecha_recogida).days
                num_semanas=0

                 #Aplicar tarifa
                if tarifa == 'De larga duración' and num_dias<=10:
                    st.error("Las tarifas de larga duración solo están disponibles para reservas superiores a 10 días")
                elif tarifa == 'De larga duración':
                    precio_tarifa = int(precio_base)*0.8
                    st.markdown(f"El precio del vehículo seleccionado, con la tarifa de larga duración es de {round(precio_tarifa,2)}€ por día.")
                    
                if tarifa == 'De fin de semana' and (fecha_recogida.weekday()!=4 or num_dias!=2):
                    st.error("Las tarifas de fin de semana solo están disponibles para reservas en fines de semana. Se debe escoger un viernes como fecha de recogida y un domingo como fecha de entrega.")
                elif tarifa == 'De fin de semana':
                    precio_tarifa = int(precio_base)*1.8
                    st.markdown(f"El precio del vehículo seleccionado, con la tarifa de fin de semana es de {round(precio_tarifa,2)}€ por fin de semana.")

                if tarifa == 'Semanal' and num_dias % 7 != 0:
                    st.error("El número de días de la reserva no es divisible por semanas")
                elif tarifa == 'Semanal':
                    precio_tarifa = int(precio_base)*6.3
                    st.markdown(f"El precio del vehículo seleccionado, con la tarifa semanal es de {round(precio_tarifa,2)}€ por semana.")
                    num_semanas = num_dias / 7
                      
                if tarifa == 'Por kilometraje':
                    precio_tarifa = int(precio_base)*0.009
                    st.markdown(f"Con esta tarifa el pago se realiza en el momento de entregar el vehículo. En estos momentos solo se tendrán que abonar posibles extras que se quieran añadir. El precio por kilometro será de {round(precio_tarifa,2)}€")

                if tarifa == 'Por día':
                    precio_tarifa = int(precio_base)
                    st.markdown(f"El precio del vehículo seleccionado, con la tarifa por día es de {round(precio_tarifa,2)}€ por día.")


                st.subheader("Otros Datos")
                client_type_selected = st.radio("Tipo de cliente", ["Cliente regular", "Cliente de negocio"])
                descuento = 0
                if client_type_selected=='Cliente de negocio':
                    descuento_selected = st.text_input("Código de descuento", "000000")
                    #descuento_selected = descuento_selected.upper()
                    if descuento_selected != "000000":
                        if int(descuento_selected) in descuentos_df["descuento"].to_list():
                            descuento = descuentos_df[descuentos_df["descuento"] == int(descuento_selected)]["porcentaje"].to_list()[0]
                            st.success(f"Código de descuento válido. Dispone usted de un descuento del {descuento}%")
                        else:
                            st.error("El código de descuento introducido no es válido.")
                #Añadir extras (Wifi, GPS, silla de seguridad y cadenas de nieve).
                st.subheader("Extras")
                wifi = st.checkbox("Wifi (+ 30€)") 
                gps = st.checkbox("GPS (+ 15€)")
                silla = st.checkbox("Silla de seguridad (+ 20€)")
                cadenas = st.checkbox("Cadenas de nieve (+ 35€)")

                st.subheader("Cantidad final a pagar")
                precio_extras = 0
                lista_extras = []
                if(wifi):
                    precio_extras+=30
                    lista_extras.append("Wifi")
                if(gps):
                    precio_extras+=15
                    lista_extras.append("GPS")
                if(silla):
                    precio_extras+=20
                    lista_extras.append("Silla de seguridad")
                if(cadenas):
                    precio_extras+=35
                    lista_extras.append("Cadenas de nieve")
                
                if tarifa == 'Por kilometraje' and (wifi or gps or silla or cadenas):
                    if descuento!=0:
                        st.markdown(f"Al tratarse de una tarifa por kilometraje, en estos momentos solo se han de abonar los extras. Se dispone de un {descuento}% de descuento, luego, cantidad a pagar:")  
                        st.header(f"{round(precio_extras-(precio_extras*descuento/100),2)}€")
                    else:
                        st.markdown(f"Al tratarse de una tarifa por kilometraje, en estos momentos solo se han de abonar los extras. Luego, cantidad a pagar:")  
                        st.header(f"{round(precio_extras-(precio_extras*descuento/100),2)}€")
                elif tarifa == 'Por kilometraje':
                    st.markdown(f"Pago a realizar tras la entrega del vehículo")

                elif tarifa == 'Por día':
                    if wifi or gps or silla or cadenas:
                            st.markdown(f"Con un total de {precio_extras}€ en extras")
                    if descuento!=0:
                        st.markdown(f"Y un {descuento}% de descuento")
                        st.header(f"{round((precio_tarifa-(precio_tarifa*descuento/100))*num_dias+precio_extras,2)}€ por {int(num_dias)} días.")
                    else:
                        st.header(f"{round((precio_tarifa)*num_dias+precio_extras,2)}€ por {int(num_dias)} días.")

                elif tarifa == 'Semanal':
                    if wifi or gps or silla or cadenas:
                            st.markdown(f"Con un total de {precio_extras}€ en extras")
                    if descuento!=0:
                        st.markdown(f"Y un {descuento}% de descuento")
                        if(num_semanas>1):
                            st.header(f"{round((precio_tarifa-(precio_tarifa*descuento/100))*num_semanas+precio_extras,2)}€ por {int(num_semanas)} semanas.")
                        else:
                            st.header(f"{round((precio_tarifa-(precio_tarifa*descuento/100))*num_semanas+precio_extras,2)}€ por una semana.")
                    else:
                        if(num_semanas>1):
                            st.header(f"{round(precio_tarifa*num_semanas+precio_extras,2)}€ por {int(num_semanas)} semanas.")
                        else:
                            st.header(f"{round(precio_tarifa*num_semanas+precio_extras,2)}€ por una semana.")

                elif tarifa == 'De fin de semana':
                    if wifi or gps or silla or cadenas:
                            st.markdown(f"Con un total de {precio_extras}€ en extras")
                    if descuento!=0:
                        st.markdown(f"Y un {descuento}% de descuento")  
                        st.header(f"{round(precio_tarifa-(precio_tarifa*descuento/100)+precio_extras,2)}€ por fin de semana.")
                    else:
                        st.header(f"{round(precio_tarifa+precio_extras,2)}€ por fin de semana.")

                elif tarifa == 'De larga duración':
                    if wifi or gps or silla or cadenas:
                        st.markdown(f"El precio incluye un total de {precio_extras}€ en extras")
                    if descuento!=0:
                        st.markdown(f"Y un {descuento}% de descuento")  
                        st.header(f"{round((precio_tarifa-(precio_tarifa*descuento/100))*num_dias+precio_extras,2)}€ por {int(num_dias)} días.")
                    else:
                        st.header(f"{round((precio_tarifa)*num_dias+precio_extras, 2)}€ por {int(num_dias)} días.")

                precio_final = round(precio_tarifa+precio_extras,2)

                # Info de pago
                st.subheader("Información de pago")

                cols = st.columns(2)
                # Seleccionar tarjeta
                tarjeta_selected = cols[0].selectbox("Seleccionar tarjeta", ["VISA", "MasterCard", "American Express"])
                # Seleccionar número de tarjeta
                num_tarjeta_selected = cols[1].text_input("Número de tarjeta", "")
                # Seleccionar código de seguridad
                cod_seguridad_selected = cols[0].text_input("Código de seguridad", "")
                # Seleccionar fecha de expiración
                fecha_expiracion_selected = cols[1].date_input("Fecha de expiración", datetime.date.today())
                # Seleccionar nombre del titular
                nombre_titular_selected = st.text_input("Nombre del titular", "")

                check_payment_value = check_payment(tarjeta_selected, num_tarjeta_selected, cod_seguridad_selected, fecha_expiracion_selected, nombre_titular_selected)

                if check_payment_value == 1:
                    st.error("Tarjeta no válida. El número de tarjeta debe tener 16 dígitos para Visa o MasterCard y 15 dígitos para American Express.")
                elif check_payment_value == 2:
                    st.error("Tarjeta no válida. El código de seguridad debe tener 3 dígitos.")
                elif check_payment_value == 3:
                    st.error("Tarjeta no válida. La fecha de expiración debe ser posterior a la fecha actual.")
                elif check_payment_value == 4:
                    st.error("Tarjeta no válida. El nombre del titular debe tener al menos 3 caracteres.")
                else:
                    info_cols = st.columns(2)
                    info_cols[0].subheader("Información de reserva")
                    with info_cols[0]:
                        st.write("Oficina de recogida: ", oficina_recogida)
                        st.write("Fecha de recogida: ", fecha_recogida)
                        st.write("Hora de recogida: ", hora_recogida)
                        st.write("Oficina de entrega: ", oficina_entrega)
                        st.write("Fecha de entrega: ", fecha_entrega)
                        st.write("Hora de entrega: ", hora_entrega)
                    info_cols[1].subheader("Información de vehículo")
                    with info_cols[1]:
                        st.write("Gama: ", car_gamma_selected)
                        st.write("Marca: ", car_brand_selected)
                        st.write("Modelo: ", car_model_selected)
                        st.write("Conducción: ", conducción_selected)
                        st.write("Número de puertas: ", num_puertas_selected)
                        st.write("Techo solar: ", solar_roof_selected)
                        st.write("Nombre del vehículo: ", car_selected)
                    info_cols = st.columns(2)
                    with info_cols[0]:
                        st.subheader("Información de pago")
                        st.write("Tarjeta seleccionada: ", tarjeta_selected)
                        st.write("Número de tarjeta: ", num_tarjeta_selected)
                        st.write("Fecha de expiración: ", fecha_expiracion_selected)
                    
                    with info_cols[1]: 
                        st.subheader("Confirmación de pedido")
                        st.write("¿Está seguro de que desea confirmar la reserva?")
                        confirmar_pedido = st.button("Confirmar reserva")

                    if confirmar_pedido:
                        id_num = len(reservas_df)
                        reservas_df.loc[id_num] = [fecha_recogida,hora_recogida,fecha_entrega,hora_entrega,oficina_recogida, oficina_entrega,car_selected, client_type_selected, tarifa, descuento, lista_extras, num_tarjeta_selected, nombre_titular_selected, precio_final,True]
                        reservas_df.to_csv("reservas_db.csv")
                       
                        if add_booking_to_user(id_num, st.session_state.get('user_id')) == 0:
                            st.success("Se ha confirmado la reserva.")
                        else:
                            st.error("No se ha podido confirmar la reserva. Vuelva a intentarlo.")
else:
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")

    st.title("Inicia Sesión para acceder a la aplicación")   