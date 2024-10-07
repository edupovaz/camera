import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class CameraApp(App):
    def build(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')

        # Componente de imagem para exibir a câmera
        self.img = Image()
        layout.add_widget(self.img)

        

        # Label para exibir a porcentagem de pixels verdes
        self.green_percentage_label = Label(text="Percentual de pixels verdes: 0%")
        layout.add_widget(self.green_percentage_label)

        # Botão de captura
        self.btn_capture = Button(text="Capturar Imagem")
        self.btn_capture.bind(on_press=self.capture_image)
        layout.add_widget(self.btn_capture)

        # Inicia a captura de vídeo
        
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)

        return layout

    def update_frame(self, dt):
        ret, frame = self.capture.read()
        pontos_folha = [[320, 100], [420, 300], [364, 400], [270, 400], [220, 300]]
                
        if ret:
            # Converte o frame do OpenCV para um formato que o Kivy pode usar
            def desenhar_guia_com_pontos(imagem, pontos):
            # Converter a lista de pontos em um array NumPy adequado para OpenCV
                pontos_array = np.array(pontos, np.int32)
                pontos_array = pontos_array.reshape((-1, 1, 2))  # Necessário para que OpenCV entenda os pontos

             # Desenhar o polígono na imagem conectando os pontos
                cv2.polylines(imagem, [pontos_array], isClosed=True, color=(255, 255, 255), thickness=6)  # Cor verde
                return imagem
            
            frame_com_guia = desenhar_guia_com_pontos(frame, pontos_folha)
            #cv2.imshow('Centralize a folha na área destacada', frame_com_guia)
            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = texture
            self.current_frame = frame

    def capture_image(self, instance):
        if hasattr(self, 'current_frame'):
            imgr = self.current_frame
            cv2.imshow("as", imgr)
            cv2.waitKey(0)
            # Ou carregue uma imagem de um arquivo:
            # imagePath = "C:\\Users\\edupo\\Downloads\\"
            # imgr = cv2.imread(imagePath + "R.jpg")
            self.analisar(imgr)
            print("Imagem capturada e analisada")

    def analisar(self, img):
        # Definição da cor alvo
        green = [0, 255, 0]
        diff = 20

        # Intervalo da cor
        boundaries = [([green[2], green[1] - diff, green[0] - diff],
                        [green[2] + diff, green[1] + diff, green[0] + diff])]

        # Redimensiona a imagem
        scalePercent = 0.5
        width = int(img.shape[1] * scalePercent)
        height = int(img.shape[0] * scalePercent)
        newSize = (width, height)
        imgrs = cv2.resize(img, newSize, None, None, None, cv2.INTER_AREA)

        mask = np.zeros(imgrs.shape[:2], dtype="uint8")
        contorno_folha = np.array([[160, 50], [210, 150], [185, 200], [135, 200], [110, 150]])
        cv2.fillPoly(mask, [contorno_folha], 255)

        imgr = cv2.bitwise_and(imgrs, imgrs, mask=mask)
        cv2.imshow("img rec",imgr)
        cv2.waitKey(0)

        for (lower, upper) in boundaries:
            lower = np.array(lower, dtype="uint8")
            upper = np.array(upper, dtype="uint8")

            mask = cv2.inRange(imgr, (1, 70, 1), (160, 255, 150))

            # Aplicando a máscara
            output = cv2.bitwise_and(imgr, imgr, mask=mask)

            # Calcula a porcentagem de pixels verdes
            ratio_green = cv2.countNonZero(mask) / (imgr.size / 3)
            colorPercent = (ratio_green * 100)
            res = np.round(colorPercent, 2)
            print('Percentual de pixels verdes:', res, '%')

            # Atualiza o texto do Label com a porcentagem de pixels verdes
            self.green_percentage_label.text = f"Percentual de pixels verdes: {res}%"

    def on_stop(self):
        # Libera a captura de vídeo quando o app é fechado
        self.capture.release()

if __name__ == '__main__':
    CameraApp().run()
