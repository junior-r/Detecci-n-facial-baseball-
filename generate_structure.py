# Importar librerías.
import os
import cv2
from matplotlib import pyplot
import imutils
from mtcnn.mtcnn import MTCNN
import time
import sqlite3
from tabulate import tabulate

count = 0
name_players = []

# Creación y conexión con la base de datos.
connect = sqlite3.connect('baseball.sqlite3')
cursor = connect.cursor()

# 18 a 36 Creación de las tablas de la Base de datos.
query = f'''
    CREATE TABLE IF NOT EXISTS Equipo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
'''
cursor.execute(query)

query = f'''
    CREATE TABLE IF NOT EXISTS Jugador (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        arm TEXT,
        equipo_id INTEGER,
        FOREIGN KEY (equipo_id) REFERENCES Equipo (id)
    )
'''
cursor.execute(query)


def login():
    # Iniciar sesión con un equipo.

    team_name = str(input("Nombre del equipo: "))

    query = f'SELECT * FROM Equipo WHERE name = ?'
    cursor.execute(query, (team_name,))
    get_data = cursor.fetchall()
    if get_data:
        menu(get_data)
    else:
        print('Nombre incorrecto. Intente de nuevo.')
        login()


def menu(get_data):
    # Presenta las opciones del programa.
    print(
        '1 - Listar jugadores, 2 - Crear jugador, 3 - Editar jugador, 4 - Borrar jugador, 5 - Registrar fotos a un jugador , 6 - Salir')
    opt = input('¿Qué desea hacer?: ')

    match opt:
        case 1 | '1':
            list_player(team_data=get_data)
        case 2 | '2':
            number_employees = int(input('Número de jugadores a crear: '))
            create_player(team_data=get_data, number_players=number_employees)
        case 3 | '3':
            edit_player(team_data=get_data)
        case 4 | '4':
            delete_player(team_data=get_data)
        case 5 | '5':
            create_carpets(team_data=get_data)
        case 6 | '6':
            return ''
        case _:
            print('Opción inválida intente de nuevo!')
            menu(get_data)


def create_team():
    # Crea los equipos.
    team_name = input("Nombre del equipo: ")
    name = input('Confirme su nombre de equipo: ')
    if team_name == name:
        try:
            query_insert = 'INSERT INTO Equipo VALUES (NULL, ?)'
            cursor.execute(query_insert, (team_name,))
            print('Equipo creado exitosamente!')
        except sqlite3.OperationalError:
            print('Ya existe su equipo')
            login()
    else:
        print('Los nombres no coinciden. Intente de nuevo.')
        create_team()


def create_player(team_data, number_players):
    # Función para crear jugadores.
    # (Parámetros.) Datos del equipo | Numero de jugadores a crear.
    global count

    while count < number_players:
        count += 1
        name_player = input(f'Nombre y apellido del jugador #{count}: ')
        arm_player = str(input(f'Brazo dominante del jugador #{count}: '))
        print()

        query = f'SELECT * FROM Jugador WHERE name = ?'
        cursor.execute(query, (name_player,))
        if cursor.fetchall():
            if name_players:
                for player in name_players:
                    if name_player in player:
                        print('Empleado ya existe!', end='\n')
                        count -= 1
            else:
                print('Empleado ya existe!', end='\n')
                count -= 1
        else:
            name_players.append((name_player, arm_player, team_data[0][0]))

            query = f'INSERT INTO Jugador VALUES (NULL, ?, ?, ?)'
            try:
                cursor.execute(query, (name_player, arm_player, team_data[0][0]))
                print('Jugador registrado', end='\n')
            except sqlite3.OperationalError as e:
                print(f'ERROR: {e}')

    return menu(get_data=team_data)


def list_player(team_data):
    # Llama a otra función para listar jugadores.
    # (Parámetros.) Datos del equipo.
    print('Lista de empleados', end='\n')
    get_data = mechanism_list_players(team_data)

    return menu(get_data=team_data)


def mechanism_list_players(team_data):
    # Lista a los jugadores.
    # (Parámetros.) Datos del equipo.
    query = f'SELECT * FROM Jugador WHERE equipo_id = ?'
    cursor.execute(query, (team_data[0][0],))
    get_data = cursor.fetchall()
    if get_data:
        headers = ['ID', 'Nombre', 'Brazo Dominante', 'ID Equipo']
        table = tabulate(get_data, headers, tablefmt='fancy_grid')
        print(table)
        return get_data
    else:
        print('No tiene empleados registrados')
        return None


def edit_player(team_data):
    # Editar los datos de un jugador.
    # (Parámetros.) Datos del equipo.
    get_data = mechanism_list_players(team_data)
    print()
    if get_data is not None:
        print('Editar jugador', end='\n')
        id = int(input('Seleccione un juf¿gador por su ID: '))
        query = f'SELECT * FROM Jugador WHERE id = ?'
        cursor.execute(query, (id,))
        player = cursor.fetchall()
        if player:
            print('1 - Nombre | 2 - Brazo', end='\n')

            field = input('Seleccione un campo a editar: ')
            if field == '1':
                field = 'name'
            elif field == '2':
                field = 'arm'
            else:
                print('No se indicó un campo válido.')
            new_value = str(input('Escriba el nuevo valor: '))
            if new_value:
                query = f'UPDATE Jugador SET ? = ? WHERE id = ?'
                cursor.execute(query, (field, new_value, player[0][0]))
                print('Actualizado éxitosamente')
                list_player(team_data)
            else:
                print('Valor inválido.')
                edit_player(team_data)
        else:
            print('No se encontró el jugador. Intente de nuevo.')
            edit_player(team_data)


def delete_player(team_data):
    # Borrar jugador.
    # (Parámetros.) Datos del equipo.
    print()
    print('Borrar jugador\n')
    get_data = mechanism_list_players(team_data)
    if get_data is not None:
        id = int(input('Seleccione un jugador por medio de su ID: '))
        if id:
            confirm = str(input('Escriba el nombre del equipo por seguridad: '))

            if team_data[0][1] == confirm:
                query = f'DELETE FROM Jugador WHERE id = ? AND equipo_id = ?'
                cursor.execute(query, (id, team_data[0][0]))
                print('Jugador eliminado exitosamente.')
                list_player(team_data)
            else:
                print('Nombre incorrecto. Intente de nuevo.')
                delete_player(team_data)
        else:
            print('No se encontró ese Jugador. Intente de nuevo.')
            delete_player(team_data)


def create_carpets(team_data):
    # Crea las carpetas necesarias para el proyecto.
    # (Parámetros.) Crea la carpeta.

    carpet = os.path.join(os.path.realpath(os.getcwd()), 'Teams', team_data[0][1], 'Players')

    if not os.path.exists(carpet):
        os.makedirs(carpet)
    query = f'SELECT * FROM Jugador WHERE equipo_id = ?'
    cursor.execute(query, (team_data[0][0],))
    players = cursor.fetchall()
    if players:
        for player in players:
            if not os.path.exists(carpet + '/' + f'{player[0]}'):  # Crea la carpeta con el ID del jugador..
                os.makedirs(carpet + '/' + f'{player[0]}')
            if not os.path.exists(carpet + '/' + f'{player[0]}' + '/' + 'Photos'): # Crea la carpeta llamada "Photos"
                os.makedirs(carpet + '/' + f'{player[0]}' + '/' + 'Photos')
            if not os.path.exists(carpet + '/' + f'{player[0]}' + '/' + 'Photos' + '/' + 'Profile'): # Crea la carpeta llamada "Profile"
                os.makedirs(carpet + '/' + f'{player[0]}' + '/' + 'Photos' + '/' + 'Profile')
            if not os.path.exists(carpet + '/' + f'{player[0]}' + '/' + 'Photos' + '/' + 'Detection'): # Crea la carpeta llamada "Detection"
                os.makedirs(carpet + '/' + f'{player[0]}' + '/' + 'Photos' + '/' + 'Detection')
        print('Carpetas creadas con éxito!')

    choose_carpet(team_data, carpet)


def choose_carpet(company_data, carpet):
    # Seleccionar carpeta a regitrar fotos.
    # (Parámetros.) Datos del equipo | Carpeta actual.
    global player
    counter = 0
    players = os.listdir(carpet)
    # --------- Select Employee
    for player in players:
        counter += 1
        print(counter, '-', player)
    choose_player = int(input('Elige un jugador por su número: '))
    query = 'SELECT * FROM Jugador WHERE id = ?'
    try:
        cursor.execute(query, (choose_player,))

        player = players[choose_player - 1]

        # Select Photo Carpet
        photo_options = os.listdir(carpet + '/' + player + '/Photos')
        count = 0
        for opt in photo_options:
            count += 1
            print(f'{count} - {opt}', end='| ')
        print()
        choose_carpet_photo = int(input(f'¿Qúe tipo de foto desea registrar?: '))
        photo_carpet = photo_options[choose_carpet_photo - 1]

        print(f'Usted eligió {photo_carpet}')
        carpet += f'/{player}/Photos/{photo_carpet}'
        if photo_carpet == 'Profile':
            # Redirige a la función para crear la foto de perfil.
            save_image_profile(carpet, player, 1)
        else:
            # Redirige a la función para crear las fotos de detección.
            save_image_profile(carpet, player, 300)
    except Exception as e:
        print(f'ERROR: {e}')
        choose_carpet(company_data, carpet)


def save_image_profile(carpet, player, limit: int):
    # Guarda la imagen de perfil o de detección en función del límite.
    # (Parámetros.) carpeta | jugador | limite
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    counter = 0

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame = imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = frame.copy()
        faces = faceClassif.detectMultiScale(gray, 1.3, 5)
        img_route = f'/{player}_{counter}.jpg'

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            rostro = auxFrame[y:y + h, x:x + w]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(carpet + img_route, rostro)
            counter += 1
        cv2.imshow('frame', frame)
        print(f'Imágen alamacenada en: {carpet + img_route}')

        img_aux = frame.copy()
        # cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # face = img_aux[y1:y2, x1:x2]
        # face = imutils.resize(face, width=150, height=150)

        k = cv2.waitKey(1)
        if k == 27 or counter >= limit:
            break

        # cv2.imshow('frame', frame)
        # cv2.imshow('face', face)

    cap.release()
    cv2.destroyAllWindows()


print('1 - Crear equipo. | 2 - Ingresar a un equipo.')
option = input('¿Qué desea hacer?: ')
if option == '1':
    create_team()
elif option == '2':
    login()
else:
    print('Opción inválida. Hasta luego.')


# Actualizar y cerrar la conexión con la base de datos.
connect.commit()
connect.close()
