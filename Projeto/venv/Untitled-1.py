import cv2
import face_recognition as fr
import os
import cvzone
from pyfirmata import Arduino, SERVO
import time

board = Arduino('/dev/ttyACM0')
board.digital[8].mode = SERVO

def rotateServo(angle):
    board.digital[8].write(angle)
    time.sleep(0.015)

ledVM = board.get_pin('d:7:o')
ledVD = board.get_pin('d:5:o')
ledAM = board.get_pin('d:6:o')

nome = []
encodes = []

lista = os.listdir('Pessoas')


for arquivo in lista:
    img = cv2.imread(f'Pessoas/{arquivo}')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodes.append(fr.face_encodings(img)[0])
    nome.append(os.path.splitext(arquivo)[0])

def compararEnc(encImg):
    for id, enc in enumerate(encodes):
        comp = fr.compare_faces([encImg],enc)
        if comp[0]:
            break
    
    return comp[0],nome[id]

print('Base carregada!')

video = cv2.VideoCapture()
ip = "http://192.168.255.106:8080/video"
video.open(ip)

faceLoc = []

while True:
    check,img = video.read()
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    try:
        faceLoc.append(fr.face_locations(imgRGB)[0])
    
    except:
        faceLoc = []

    if faceLoc:
        ledAM.write(1)
        y1,x2,y2,x1 = faceLoc[-1]
        w, h = x2-x1, y2-y1
        cvzone.cornerRect(img,(x1,y1,w,h), colorR=(255,0,0))
        cvzone.putTextRect(img, 'Analisando...',(50,50),colorR=(255,0,0))

    if len(faceLoc)>20:
        encodeImg = fr.face_encodings(imgRGB)[0]
        comp,nome = compararEnc(encodeImg)

        if comp:
            cvzone.putTextRect(img, 'Acesso Liberado',(50,50),colorR=(0,255,0))
            ledAM.write(0)
            ledVD.write(1)
            rotateServo(130)
            time.sleep(2)
            rotateServo(0)
            ledVD.write(0)

        else:
            cvzone.putTextRect(img, 'Acesso Negado',(50,50),colorR=(0,0,255))
            ledVM.write(1)
            ledAM.write(0)
            time.sleep(2)
            ledVM.write(0)



    cv2.imshow('img',img)
    cv2.waitKey(1)
