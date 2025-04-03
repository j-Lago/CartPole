import pygame
import sys
import math
import random

# Inicialização
pygame.init()

# Configurações de tela
WIDTH, HEIGHT = 1200, 800  # Tamanho maior da janela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Foguete com Dois Motores")

# Configurações do foguete
rocket_width, rocket_height = 20, 50
rocket_x, rocket_y = WIDTH // 2, 50
velocity_x, velocity_y = 0, 0
gravity = 0.2
motor_vertical_power = -0.5  # Aumentei a força do motor vertical
motor_horizontal_power = 0.2
angle = 0
angular_velocity = 0  # Velocidade angular do foguete

# Configurações de tolerância
max_impact_velocity = 5.0  # Velocidade máxima tolerada para vencer

# Lista de partículas de exaustão
exhaust_particles = []

# Inicializa o joystick
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()


# Função para exibir mensagem de vitória/derrota
def display_message(text):
    font = pygame.font.Font(None, 74)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False


# Função para exibir HUD
def draw_hud(velocity_x, velocity_y, angle):
    font = pygame.font.Font(None, 36)
    velocity = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
    text_velocity = f"Velocidade: {velocity:.2f} m/s"
    text_angle = f"Inclinação: {angle:.1f}°"

    # Renderiza os textos no HUD
    velocity_surface = font.render(text_velocity, True, (255, 255, 255))
    angle_surface = font.render(text_angle, True, (255, 255, 255))
    screen.blit(velocity_surface, (10, 10))
    screen.blit(angle_surface, (10, 50))


# Relógio para taxa fixa de FPS
clock = pygame.time.Clock()


# Função para adicionar partículas de exaustão
def add_exhaust_particles(x, y, direction):
    for _ in range(5):  # Número de partículas geradas
        exhaust_particles.append({
            "x": x + random.randint(-5, 5),
            "y": y + random.randint(-5, 5),
            "size": random.randint(2, 5),
            "velocity_x": random.uniform(-1, 1) + direction[0] * -2,
            "velocity_y": random.uniform(1, 3) + direction[1] * -2,
            "color": (255, random.randint(100, 200), 0)  # Tons de laranja
        })


# Função para atualizar e desenhar partículas de exaustão
def update_exhaust_particles():
    for particle in exhaust_particles:
        particle["x"] += particle["velocity_x"]
        particle["y"] += particle["velocity_y"]
        particle["size"] -= 0.1  # Reduz o tamanho para desaparecer
    # Remove partículas muito pequenas
    exhaust_particles[:] = [p for p in exhaust_particles if p["size"] > 0]

    for particle in exhaust_particles:
        pygame.draw.circle(screen, particle["color"], (int(particle["x"]), int(particle["y"])), int(particle["size"]))


# Loop principal do jogo
while True:
    # Redefine configurações para reinício
    rocket_x, rocket_y = WIDTH // 2, 50
    velocity_x, velocity_y = 0, 0
    angle = 0
    angular_velocity = 0
    running = True

    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Verifica o estado do joystick
        vertical_thrust = 0
        horizontal_thrust = 0
        if joystick:
            vertical_thrust = joystick.get_axis(
                1) * -motor_vertical_power  # Controle analógico esquerdo (empuxo vertical)
            horizontal_thrust = joystick.get_axis(
                0) * motor_horizontal_power  # Controle analógico direito (empuxo horizontal somente em x)

        # Atualiza o ângulo do foguete com base no torque gerado pelos motores
        torque = -horizontal_thrust * 0.15  # Ajuste da intensidade do torque
        angular_velocity += torque
        angle += angular_velocity
        angle %= 360  # Mantém o ângulo dentro de 0 a 360 graus

        # Atualização da física
        velocity_y += gravity  # Gravidade
        velocity_x += horizontal_thrust
        velocity_y += vertical_thrust

        rocket_x += velocity_x
        rocket_y += velocity_y

        # Adiciona partículas de exaustão para cada motor
        if vertical_thrust != 0:
            add_exhaust_particles(
                rocket_x,
                rocket_y + rocket_height // 2,
                [0, -1]
            )
        if horizontal_thrust != 0:
            add_exhaust_particles(
                rocket_x,
                rocket_y + rocket_height // 2,
                [-1 if horizontal_thrust > 0 else 1, 0]
            )

        # Verifica condições de fim de jogo
        if rocket_y + rocket_height // 2 >= HEIGHT:
            total_velocity = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
            if total_velocity > max_impact_velocity:  # Tolerância aumentada
                display_message("Você perdeu!")
            else:
                display_message("Você venceu!")
            running = False

        # Limita o foguete dentro da tela
        rocket_x = max(0, min(WIDTH, rocket_x))
        rocket_y = max(0, min(HEIGHT, rocket_y))

        # Desenho do foguete com rotação
        rocket_surface = pygame.Surface((rocket_width, rocket_height), pygame.SRCALPHA)
        pygame.draw.rect(rocket_surface, (255, 0, 0), (0, 0, rocket_width, rocket_height))
        rotated_rocket = pygame.transform.rotate(rocket_surface, -angle)
        rect = rotated_rocket.get_rect(center=(rocket_x, rocket_y))
        screen.blit(rotated_rocket, rect.topleft)

        # Atualização e desenho das partículas de exaustão
        update_exhaust_particles()

        # Desenha o HUD
        draw_hud(velocity_x, velocity_y, angle)

        # Atualização da tela
        pygame.display.flip()
        clock.tick(60)

    display_message("Pressione Enter para jogar novamente!")