import ast
from datetime import time
import datetime
from traceback import print_tb
import pandas as pd


# Returns: 
# 0: Fecha y hora correctas
# 1: Hora de recogida no válida
# 2: Hora de entrega no válida
# 3: Fecha de recogida igual a fecha de entrega y hora de recogida mayor a hora de entrega
# 4: Fecha de recogida superior a fecha de entrega


def check_datetime(fecha_recogida, hora_recogida, fecha_entrega, hora_entrega):
    # Si fecha es hoy
    if fecha_recogida == datetime.date.today():
        if hora_recogida < datetime.datetime.now().time() :
            return 5


    if (fecha_recogida < fecha_entrega):
        return check_hora(hora_recogida, hora_entrega)
    elif fecha_recogida == fecha_entrega:
        if (hora_recogida < hora_entrega):
            return check_hora(hora_recogida, hora_entrega)

        else:
            # Fecha de recogida igual a fecha de entrega y hora de recogida mayor a hora de entrega
            return 3
    else:
        # Fecha incorrrecta: la fecha de recogida es superior a la fecha de entrega
        return 4


def check_hora(hora_recogida, hora_entrega):
    if (time(8,0,0) <= hora_recogida <= time(22,0,0)):
        if (time(8,0,0) <= hora_entrega <= time(22,0,0)):
            return 0
        else:
            # Hora de entrega no válida
            return 2
    else:
        # Hora de recogida no válida
        return 1




def get_available_cars(oficina):
    car_df = pd.read_csv('car_db.csv')
    available_cars_df = pd.DataFrame(columns=car_df.columns)
    for i, row in car_df.iterrows():
        if row['Oficina'] == oficina:
            available_cars_df.loc[len(available_cars_df)] = row

    return available_cars_df



def check_payment(tarjeta_selected, num_tarjeta_selected, cod_seguridad_selected, fecha_expiracion_selected, nombre_titular_selected):
                if tarjeta_selected == "VISA":
                    if len(num_tarjeta_selected) != 16:
                        return 1
                elif tarjeta_selected == "MasterCard":
                    if len(num_tarjeta_selected) != 16:
                        return 1
                elif tarjeta_selected == "American Express":
                    if len(num_tarjeta_selected) != 15:
                        return 1
                if len(cod_seguridad_selected) != 3:
                    return 2
                if fecha_expiracion_selected < datetime.date.today():
                    return 3
                if len(nombre_titular_selected) <= 2:
                    return 4
                return 0


def check_user_and_password(usuario, contraseña="", password=True, email = "", drop=""):
    users_df = pd.read_csv('users_db.csv')

    if drop != "":
        users_df.drop(drop, inplace=True)

    # Buscamos correspondencias
    for i, row in users_df.iterrows():
        # Si no queremos comprobar la contraseña
        if not password:
            if (row['usuario'] == usuario or row["email"] == email):
                return row["ID"]

        elif (row['usuario'] == usuario or row["email"] == usuario) and row['contrasena'] == contraseña:
            return row["ID"]
    else:
        return -1

def add_user(usuario, contraseña, email, admin):
    users_df = pd.read_csv('users_db.csv', index_col=0)
    user_id = len(users_df)
    users_df.loc[len(users_df)] = [usuario,email,contraseña,admin,[]]
    users_df.to_csv('users_db.csv')
    return 0, user_id

# NAVIGATION CONTROL
def navigation(st, page_list):
    if st.session_state.get('page') == "Alquilar Coche":
        page = "Alquilar Coche"
        page = sidebar(st, page_list)

    elif st.session_state.get('page') == "Modificar datos de usuario":
        page = "Modificar datos de usuario"
        page = sidebar(st, page_list)

    elif st.session_state.get('page') == "Gestionar oficinas":
        page = "Gestionar oficinas"
        page = sidebar(st, page_list)

    elif st.session_state.get('page') == "Gestionar coches":
        page = "Gestionar coches"
        page = sidebar(st, page_list)

    elif st.session_state.get('page') == "Mis reservas":
        page = "Mis reservas"
        page = sidebar(st, page_list)

    elif st.session_state.get('page') == "Comprobar facturación":
        page = "Comprobar facturación"
        page = sidebar(st, page_list)

    elif st.session_state.get('page') == "Registro usuario":
        page = "Registro usuario"

    else:
        page = "Inicio de Sesión"

    return page



# SIDEBAR
def sidebar(st, page_list):
    with st.sidebar:
        page = st.selectbox("Navegación", page_list)
        # st.sidebar.markdown("#")
        close_session = st.button("Cerrar sesión")
        if close_session:
            st.session_state.clear()
            st.experimental_rerun()
        return page



def check_register_data(st,email,usuario, contraseña,contraseña2,admin,code, drop=""):
    res = True
    
    if (admin == True) & (code != "admin"):
        st.error("Código de administrador incorrecto.")

    # check if email is empty
    if len(email) == 0:
        st.error("El email no puede estar vacío.")
        res = False
    # check if user is empty
    elif len(usuario) == 0:
        st.error("El usuario no puede estar vacío.")
        res = False

    # check if password is empty
    elif len(contraseña) == 0:
        st.error("La contraseña no puede estar vacía.")
        res = False

    # EMAIL VÁLIDO
    elif "@" not in email:
        st.error("El email no es válido.")
        res = False

    # USUARIO VÁLIDO
    user_id = check_user_and_password(usuario, email=email, password=False, drop=drop)
    if user_id != -1:
        st.error("Usuario o email ya existente.")
        res = False

    elif contraseña != contraseña2:
        st.error("Las contraseñas no coinciden.")
        res = False


    return res



def get_user_data(user_id):
    users_df = pd.read_csv('users_db.csv')
    old_email = users_df.loc[user_id]["email"]
    old_usuario = users_df.loc[user_id]["usuario"]
    old_contraseña = users_df.loc[user_id]["contrasena"]
    return old_email, old_usuario, old_contraseña

def edit_user(st,usuario, contraseña, email, user_id):
    users_df = pd.read_csv('users_db.csv', index_col=0)
    users_df.at[user_id,"usuario"] = usuario
    users_df.at[user_id,"email"] = email
    users_df.at[user_id,"contrasena"] = contraseña
    users_df.to_csv('users_db.csv')
    return 0

def delete_user(user_id):
    users_df = pd.read_csv('users_db.csv', index_col=0)
    users_df.drop(user_id, inplace=True)
    users_df.reset_index(drop=True, inplace=True)
    users_df.to_csv('users_db.csv',)
    return 0


def is_admin(user_id):
    if user_id == None:
        return False
    users_df = pd.read_csv('users_db.csv', index_col=0)
    return users_df.at[user_id,"administrador"]


def add_office(name):
    offices_df = pd.read_csv('oficinas_db.csv', index_col=0)

    # Comprobar que el nombre no está cogido
    for i, row in offices_df.iterrows():
        if row['Nombre'] == name:
            return 1
    # add new row
    offices_df.loc[len(offices_df)] = [name]
    offices_df.to_csv('oficinas_db.csv')
    return 0


def delete_office(name):
    offices_df = pd.read_csv('oficinas_db.csv', index_col=0)
    offices_df.drop(name, inplace=True)
    offices_df.reset_index(drop=True, inplace=True)
    offices_df.to_csv('oficinas_db.csv',)
    return 0


def edit_office(office_id, new_name):
    offices_df = pd.read_csv('oficinas_db.csv', index_col=0)
    # Comprobar que el nombre no está cogido
    offices_df.at[office_id,"Nombre"] = new_name
    offices_df.to_csv('oficinas_db.csv')
    return 0

def add_car(name,marca,modelo,category,manual,num_puertas,solar_roof,oficina,precio_por_dia):
    cars_df = pd.read_csv('car_db.csv', index_col=0)

    # Comprobar que el nombre no está cogido
    for i, row in cars_df.iterrows():
        if row['Name'] == name:
            return 1

    cars_df.loc[len(cars_df)] = [name,marca,modelo,category,manual,num_puertas,solar_roof,oficina,precio_por_dia]
    cars_df.to_csv('car_db.csv')
    return 0

def delete_car(car_id):
    cars_df = pd.read_csv('car_db.csv', index_col=0)
    cars_df.drop(car_id, inplace=True)
    cars_df.reset_index(drop=True, inplace=True)
    cars_df.to_csv('car_db.csv',)
    return 0

def edit_car(car_index, name,marca,modelo,category,manual,num_puertas,solar_roof,oficina,precio_por_dia):
    cars_df = pd.read_csv('car_db.csv', index_col=0)
    cars_df.at[car_index,"Name"] = name
    cars_df.at[car_index,"Marca"] = marca
    cars_df.at[car_index,"Modelo"] = modelo
    cars_df.at[car_index,"Category"] = category
    cars_df.at[car_index,"Manual"] = manual
    cars_df.at[car_index,"Num_Puertas"] = num_puertas
    cars_df.at[car_index,"Solar_Roof"] = solar_roof
    cars_df.at[car_index,"Oficina"] = oficina
    cars_df.at[car_index,"Precio_por_Dia"] = precio_por_dia
    cars_df.to_csv('car_db.csv')
    return 0


def get_user_bookings(client_id):
    if client_id == None:
        return []
    users_df = pd.read_csv('users_db.csv', index_col=0)
    reservas_string = users_df.at[client_id,"reservas"]
    # convert from list in string to list
    reservas_list = ast.literal_eval(reservas_string)
    return reservas_list

def delete_user_booking(client_id, booking_id):
    users_df = pd.read_csv('users_db.csv', index_col=0)
    reservas_string = users_df.at[client_id,"reservas"]
    # convert from list in string to list
    reservas_list = ast.literal_eval(reservas_string)
    reservas_list.remove(booking_id)
    users_df.at[client_id,"reservas"] = reservas_list
    users_df.to_csv('users_db.csv')

    # delete booking
    reservas_df = pd.read_csv('reservas_db.csv', index_col=0)
    reservas_df.at[booking_id,"Active"] = False
    reservas_df.to_csv('reservas_db.csv')

    return 0

def get_bookings_for_period(start_date, end_date):
    reservas_df = pd.read_csv('reservas_db.csv')
    # convert fecha recogida to datetime
    reservas_df['Fecha Recogida'] = pd.to_datetime(reservas_df['Fecha Recogida']).dt.date
    reservas_df = reservas_df[reservas_df['Fecha Recogida'] >= start_date]
    reservas_df = reservas_df[reservas_df['Fecha Recogida'] <= end_date]
    return reservas_df


def add_booking_to_user(id_num, user_id):
    users_df = pd.read_csv('users_db.csv', index_col=0)
    reservas_string = users_df.at[user_id,"reservas"]
    # convert from list in string to list
    reservas_list = ast.literal_eval(reservas_string)
    if reservas_list == None:
        reservas_list = []
    reservas_list.append(id_num)
    users_df.at[user_id,"reservas"] = reservas_list
    users_df.to_csv('users_db.csv')
    return 0