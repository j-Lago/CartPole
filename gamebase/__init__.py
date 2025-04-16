from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = '0.0.0'


from .canvas import Canvas, remap
from .basescreen import BaseScreen
from .filters import MediaMovel
from .image import Image
from .inputs import BaseInput, Joystick, LinearController, NoneInput
from .mouse import Mouse, MouseScroll, MouseButton
from .particles import Particles, Particle, TextParticle, BallParticle
from .popup import PopUpText, PopUp
from .scope import Scope
from .lerp import *
from .utils import *

