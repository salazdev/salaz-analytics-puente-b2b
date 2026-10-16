import cv2
import numpy as np

print("¡Entorno configurado correctamente!")
print("Versión de OpenCV instalada:", cv2.__version__)

# Intentar cargar la imagen de prueba
img = cv2.imread("plano_test.png")

if img is not None:
    alto, ancho, canales = img.shape
    print(f"Éxito: Plano cargado con dimensiones {ancho}x{alto} píxeles.")
else:
    print("Nota: Coloca una imagen llamada 'plano_test.png' en la carpeta para medirla.")