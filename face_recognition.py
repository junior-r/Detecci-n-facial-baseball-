import sqlite3
import time
import cv2
import os
import tkinter
from PIL import ImageTk, Image


connect = sqlite3.connect('baseball.sqlite3')
cursor = connect.cursor()

player = ''
# team = input('Nombre del equipo: ')
base_path = os.path.join(os.path.realpath(os.getcwd()), 'Teams')
teams = []
imagePaths = []

for team in os.listdir(base_path):
    teams.append(os.path.join(base_path, team, 'Players'))


for path in teams:
    dataPath = path + '/Players/'  # Cambia a la ruta donde hayas almacenado Data
    for p in os.listdir(path):
        imagePaths.append(p)
    # print('imagePaths =', imagePaths)

# print(imagePaths)
face_recognizer = cv2.face.EigenFaceRecognizer_create()
# face_recognizer = cv2.face.FisherFaceRecognizer_create()
# face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# ---------- Leyendo el modelo
face_recognizer.read(os.path.realpath(os.getcwd()) + '/modeloEigenFace.xml')
# face_recognizer.read(base_path + 'modeloFisherFace.xml')
# face_recognizer.read(base_path + 'modeloLBPHFace.xml')

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture('Video.mp4')

face_classif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    if not ret: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    auxFrame = gray.copy()
    faces = face_classif.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        face = auxFrame[y:y + h, x:x + w]
        face = cv2.resize(face, (150, 150), interpolation=cv2.INTER_CUBIC)
        result = face_recognizer.predict(face)
        cv2.putText(frame, '{}'.format(result), (x, y - 5), 1, 1.3, (255, 255, 0), 1, cv2.LINE_AA)

        # EigenFaces
        if result[1] < 5700:
            query = 'SELECT * FROM Jugador WHERE id = ?'

            cursor.execute(query, (int(imagePaths[result[0]]), ))
            player = cursor.fetchall()

            cv2.putText(frame, '{}'.format(player[0][1]), (x, y - 25), 2, 1.1, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            cv2.putText(frame, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        '''
        # FisherFace
        if result[1] < 500:
            cv2.putText(frame,'{}'.format(imagePaths[result[0]]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
        else:
            cv2.putText(frame,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)

        # LBPHFace
        if result[1] < 70:
            cv2.putText(frame,'{}'.format(imagePaths[result[0]]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
        else:
            cv2.putText(frame,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
            cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)
        '''
    cv2.imshow('frame', frame)
    k = cv2.waitKey(1)
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()


if player:
    # print(player)
    ventana = tkinter.Tk()
    ventana.title('Datos del Jugador.')
    ventana.geometry("600x400")

    # -------- Get team info.
    id_team = player[0][3]
    query = 'SELECT name FROM Equipo WHERE id = ?'
    cursor.execute(query, (int(id_team),))
    equipo = cursor.fetchall()

    # -------- Getting image profile route.
    img_path = os.path.realpath(os.path.join(base_path, str(equipo[0][0]), 'Players', str(player[0][0]), 'Photos', 'Profile'))
    img_profile = os.listdir(img_path)[0]
    img_route = os.path.join(img_path, img_profile)
    # print(img_route)

    # -------- Loading image on Tkinter
    img = ImageTk.PhotoImage(Image.open(img_route))
    lbl_img = tkinter.Label(ventana, image=img)
    lbl_img.pack()

    etiqueta = tkinter.Label(ventana, text=f"Nombre: {player[0][1]}")
    etiqueta.pack()

    etiqueta2 = tkinter.Label(ventana, text=f"Brazo dominante: {player[0][2]}")
    etiqueta2.pack()

    etiqueta3 = tkinter.Label(ventana, text=f"Equipo: {equipo[0][0]}")
    etiqueta3.pack()

    ventana.mainloop()


connect.commit()
connect.close()
