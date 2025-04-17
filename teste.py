import pygame

command_registry = {}


def bind_command(name, keyboard=None, joystick=None, joystick_axis=None):
    command_registry[name] = {'keyboard': keyboard, 'joystick': joystick, 'joystick_axis': joystick_axis}

bind_command(name='start', keyboard=pygame.K_RETURN, joystick=0)
bind_command(name='stop', keyboard=pygame.K_ESCAPE, joystick=1)

def handle_command(name):
    print(f'{command_registry}')


if __name__ == '__main__':
    handle_command('start')