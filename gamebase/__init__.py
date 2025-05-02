from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = '0.0.0'

from .drag_lock import DragLock
from .canvas import Canvas, remap, blit_with_aspect_ratio
from .basescreen import BaseScreen
from .filters import MediaMovel
from .image import Image
from .inputs import BaseInput, Joystick, LinearController, NoneInput, InputPool, Keyboard
from .mouse import Mouse, MouseScroll, MouseButton
from .particles import Particles, Particle, TextParticle, BallParticle
from .collidable_particle import BallCollidableParticle
from .popup import PopUpText, PopUp
from .scope import Scope
from .gameclock import Clock, Timer
from .lerp import *
from .utils import *
from .basebutton import BaseButton
from .button import Button
from .progressbar import ProgressBar
from .event_enum import UserEventEnum
from .slider import Slider
from .frame import Frame


