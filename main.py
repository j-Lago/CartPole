import assets
from game import Game

if __name__ == '__main__':
    game = Game('CartPole',
                (1600, 900),  # None -> fullscreen
                60,
                assets.sounds,
                assets.fonts,
                assets.images,
                45,
                18,
                training_mode=False,
                )
    