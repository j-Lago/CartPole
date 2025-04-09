import pygame
import time

# Inicializar o pygame
pygame.init()
t1 = time.perf_counter()
dt = 0.0

# Configurar a tela
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Texto no Centro")

# Configurar fonte e texto
font = pygame.font.Font(None, 74)  # Fonte padrão, tamanho 74


# Configurar relógio para taxa de quadros fixa
clock = pygame.time.Clock()

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Atualizar a tela
    screen.fill((0, 0, 0))  # Preencher a tela com preto

    text = font.render(f'{dt*1000:.1f} ms', True, (255, 255, 255))  # Texto branco
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))  # Centralizar texto
    screen.blit(text, text_rect)  # Desenhar o texto no centro
    pygame.display.flip()  # Trocar buffers para exibir as mudanças

    t2 = time.perf_counter()
    dt = t2 - t1

    # Limitar FPS a 60
    clock.tick(60)
    t1 = time.perf_counter()

pygame.quit()