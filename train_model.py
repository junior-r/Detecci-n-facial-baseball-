import cv2
import os
import numpy as np


# team = input('Nombre del equipo: ')
base_path = os.path.join(os.path.realpath(os.getcwd()), 'Teams')
teams = []

labels = []
facesData = []
label = 0

for team in os.listdir(base_path):
    teams.append(os.path.join(base_path, team))

for path in teams:
    dataPath = path + '/Players'  # Cambia a la ruta donde hayas almacenado Data
    peopleList = os.listdir(dataPath)
    print('Lista de personas: ', peopleList)

    for nameDir in peopleList:
        personPath = dataPath + '/' + nameDir + '/Photos/Detection/'
        print('Leyendo las imágenes')
        for fileName in os.listdir(personPath):
            print('Rostros: ', nameDir + '/' + fileName)
            labels.append(label)
            facesData.append(cv2.imread(personPath + '/' + fileName, 0))
            # image = cv2.imread(personPath+'/'+fileName,0)
            # cv2.imshow('image',image)
            # cv2.waitKey(10)
        label = label + 1
    # print('labels= ',labels)
    # print('Número de etiquetas 0: ',np.count_nonzero(np.array(labels)==0))
    # print('Número de etiquetas 1: ',np.count_nonzero(np.array(labels)==1))


# Métodos para entrenar el reconocedor
face_recognizer = cv2.face.EigenFaceRecognizer_create()
# face_recognizer = cv2.face.FisherFaceRecognizer_create()
# face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Entrenando el reconocedor de rostros
print("Entrenando...")
face_recognizer.train(facesData, np.array(labels))

# Almacenando el modelo obtenido
face_recognizer.write(os.path.realpath(os.getcwd()) + '/modeloEigenFace.xml')
# face_recognizer.write(base_path + 'modeloFisherFace.xml')
# face_recognizer.write(base_path + 'modeloLBPHFace.xml')
print("Modelo almacenado...")
