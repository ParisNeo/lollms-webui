from enum import Enum
from ascii_colors import ASCIIColors
class ROLE_CHANGE_DECISION(Enum):
    """Roles change detection."""
    
    MOVE_ON = 0
    """The received chunk is a normal chunk so move on."""
    
    PROGRESSING = 1
    """Started receiving Role change."""

    ROLE_CHANGED = 2
    """Role change detected."""

    FALSE_ALERT = 3
    """False alert (didn't detect the full role change)."""

class ROLE_CHANGE_OURTPUT:
    status:ROLE_CHANGE_DECISION
    value:str=""
    def __init__(self, status, value='') -> None:
        self.status = status
        self.value = value

class RECEPTION_MANAGER:
    done:bool=False
    chunk:str=""
    new_role:str=""
    reception_buffer:str=""
    def new_chunk(self, chunk):
        self.chunk = chunk
        if chunk=="!" and self.new_role == "":
            self.new_role+=chunk
            return ROLE_CHANGE_OURTPUT(ROLE_CHANGE_DECISION.PROGRESSING)
        elif self.new_role != "":
            if self.new_role=="!" and chunk=="@":
                self.new_role+=chunk
                return ROLE_CHANGE_OURTPUT(ROLE_CHANGE_DECISION.PROGRESSING)
            elif self.new_role=="!@" and chunk==">":
                self.new_role=""
                self.done=True
                ASCIIColors.yellow("Delected end of sentence")
                return ROLE_CHANGE_OURTPUT(ROLE_CHANGE_DECISION.ROLE_CHANGED, self.reception_buffer)
            else:
                rc = ROLE_CHANGE_OURTPUT(ROLE_CHANGE_DECISION.FALSE_ALERT, self.reception_buffer)
                self.reception_buffer += self.new_role      
                return rc
        self.reception_buffer += chunk
        return ROLE_CHANGE_OURTPUT(ROLE_CHANGE_DECISION.MOVE_ON)

