import pyautogui
import random
import time

def ghost_mouse(duration_seconds=5):
    """Mueve el mouse a posiciones aleatorias por un tiempo limitado."""
    print("Iniciando simulación. El mouse se moverá solo por 5 segundos...")
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        # Obtiene el tamaño actual de tu pantalla en Windows
        screen_width, screen_height = pyautogui.size()
        
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        
        # Mueve el mouse a la nueva coordenada en 0.2 segundos
        pyautogui.moveTo(x, y, duration=0.2)
        
    print("Simulación terminada. Control devuelto.")

# --- PUNTO DE ENTRADA DEL SCRIPT ---
# Esto es lo que faltaba: la orden real de ejecución.
if __name__ == "__main__":
    # Esperamos 2 segundos antes de empezar para que puedas soltar el mouse
    time.sleep(2) 
    ghost_mouse(5)