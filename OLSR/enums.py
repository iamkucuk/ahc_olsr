from enum import Enum

class OLSREventTypes(Enum):
    HELLO = "hello"
    TC = "topology_control"

class Willingness(Enum):
    WILL_NEVER = 0
    WILL_LOW = 1
    WILL_DEFAULT = 3
    WILL_HIGH = 7
    WILL_ALWAYS = 255