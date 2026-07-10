import pygame
import tkinter as tk
from tkinter import ttk
import threading

frequency = 1.0  
is_running = False
signal_high = False
history = []  
request_save = False  


class ClockGenerator:
    def __init__(self):
        self.last_switch = pygame.time.get_ticks()

    def update(self):
        global signal_high, is_running
        if not is_running:
            return False

        current_time = pygame.time.get_ticks()
        half_period = 500 / frequency  

        if current_time - self.last_switch >= half_period:
            signal_high = not signal_high
            self.last_switch = current_time
            return True
        return False

def start_gui():
    global frequency, is_running, request_save

    root = tk.Tk()
    root.title("Управление генератором")
    root.geometry("380x260")
    root.resizable(False, False)

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Управление")

    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Инфо")
    ttk.Label(tab2, text="Генератор тактовых импульсов ЦП", 
              padding=30, justify="center", font=("Arial", 11)).pack()

    def on_scale(val):
        global frequency
        frequency = float(val)
        lbl_freq.config(text=f"Частота: {frequency:.1f} Гц")

    def toggle_start():
        global is_running
        is_running = not is_running
        btn_start.config(text="Стоп" if is_running else "Старт")

    def trigger_save():
        global request_save
        request_save = True

    lbl_freq = ttk.Label(tab1, text="Частота: 1.0 Гц", font=("Arial", 12))
    lbl_freq.pack(pady=15)

    scale = ttk.Scale(tab1, from_=1.0, to=5.0, value=1.0, orient="horizontal", command=on_scale, length=250)
    scale.pack(pady=5)

    btn_start = ttk.Button(tab1, text="Старт", command=toggle_start)
    btn_start.pack(pady=10)

    btn_save = ttk.Button(tab1, text="Сохранить график (PNG)", command=trigger_save)
    btn_save.pack(pady=5)

    root.mainloop()

gui_thread = threading.Thread(target=start_gui, daemon=True)
gui_thread.start()

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Осциллограмма тактового сигнала")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 44, bold=True)
small_font = pygame.font.SysFont("Arial", 14)

generator = ClockGenerator()
running = True

def save_graph_to_image():
    filename = "clock_signal.png"
    pygame.image.save(screen, filename)
    print(f"[УСПЕШНО] График сохранен в файл: {filename}")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_graph_to_image()

    if request_save:
        save_graph_to_image()
        request_save = False

    generator.update()

    screen.fill((30, 30, 30))

    pygame.draw.line(screen, (60, 60, 60), (60, 200), (WIDTH - 40, 200), 1)
    pygame.draw.line(screen, (60, 60, 60), (60, 300), (WIDTH - 40, 300), 1)
    screen.blit(small_font.render("1 (High)", True, (120, 120, 120)), (10, 192))
    screen.blit(small_font.render("0 (Low)", True, (120, 120, 120)), (10, 292))

    if is_running:
        history.append(1 if signal_high else 0)
    else:
        history.append(history[-1] if history else 0)
    
    if len(history) > (WIDTH - 100):
        history.pop(0)

    points = []
    for i, val in enumerate(history):
        x = 60 + i
        y = 300 - (val * 100)
        
        if i > 0 and history[i] != history[i-1]:
            prev_y = 300 - (history[i-1] * 100)
            points.append((x, prev_y))
            
        points.append((x, y))

    if len(points) > 1:
        pygame.draw.lines(screen, (0, 255, 0), False, points, 3)

    if is_running:
        text_str = "TICK" if signal_high else "TOCK"
        text_color = (0, 255, 100) if signal_high else (255, 50, 50)
        text_surface = font.render(text_str, True, text_color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 100))
        screen.blit(text_surface, text_rect)
    else:
        text_surface = font.render("ПАУЗА", True, (150, 150, 150))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, 100))
        screen.blit(text_surface, text_rect)

    help_text = small_font.render("Нажмите 'S' в этом окне или кнопку в GUI для сохранения PNG", True, (100, 100, 100))
    screen.blit(help_text, (60, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()