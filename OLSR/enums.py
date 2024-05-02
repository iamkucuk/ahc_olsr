from enum import Enum

class OLSREventTypes(Enum):
    """
    Enum class representing different event types in OLSR protocol.
    """
    HELLO = "hello"
    TC = "topology_control"

class Willingness(Enum):
    """
    Enum class representing different willingness levels in OLSR protocol.
    """
    WILL_NEVER = 0
    WILL_LOW = 1
    WILL_DEFAULT = 3
    WILL_HIGH = 7
    WILL_ALWAYS = 255