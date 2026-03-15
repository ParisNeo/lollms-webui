from enum import Enum
class MSG_TYPE(Enum):
    # Messaging
    MSG_TYPE_CONTENT                   = 1 # A full message (for some personality the answer is sent in bulk)
    MSG_TYPE_CONTENT_INVISIBLE_TO_AI   = 2 # A full message (for some personality the answer is sent in bulk)
    MSG_TYPE_CONTENT_INVISIBLE_TO_USER = 3 # A full message (for some personality the answer is sent in bulk)

class MSG_OPERATION_TYPE(Enum):
    # Conditionning
    MSG_OPERATION_TYPE_ADD_CHUNK    = 0 # Add a chunk to the current message
    MSG_OPERATION_TYPE_SET_CONTENT  = 1 # sets the content of current message
    MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI      = 2 # sets the content of current message as invisible to ai
    MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER    = 3 # sets the content of current message as invisible to user
    # Informations
    MSG_OPERATION_TYPE_EXCEPTION              = 4 # An exception occured
    MSG_OPERATION_TYPE_WARNING                = 5 # A warning occured
    MSG_OPERATION_TYPE_INFO                   = 6 # An information to be shown to user

    # Steps
    MSG_OPERATION_TYPE_STEP                   = 7 # An instant step (a step that doesn't need time to be executed)
    MSG_OPERATION_TYPE_STEP_START             = 8 # A step has started (the text contains an explanation of the step done by he personality)
    MSG_OPERATION_TYPE_STEP_PROGRESS          = 9 # The progress value (the text contains a percentage and can be parsed by the reception)
    MSG_OPERATION_TYPE_STEP_END_SUCCESS       = 10# A step has been done (the text contains an explanation of the step done by he personality)
    MSG_OPERATION_TYPE_STEP_END_FAILURE       = 11# A step has been done (the text contains an explanation of the step done by he personality)

    #Extra
    MSG_OPERATION_TYPE_JSON_INFOS             = 12# A JSON output that is useful for summarizing the process of generation used by personalities like chain of thoughts and tree of thooughts
    MSG_OPERATION_TYPE_REF                    = 13# References (in form of  [text](path))
    MSG_OPERATION_TYPE_CODE                   = 14# A javascript code to execute
    MSG_OPERATION_TYPE_UI                     = 15# A vue.js component to show (we need to build some and parse the text to show it)

    #Commands
    MSG_OPERATION_TYPE_NEW_MESSAGE            = 16# A new message
    MSG_OPERATION_TYPE_FINISHED_MESSAGE       = 17# End of current message

CONTENT_OPERATION_TYPES = [MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER]

class SENDER_TYPES(Enum):
    SENDER_TYPES_USER               = 0 # Sent by user
    SENDER_TYPES_AI                 = 1 # Sent by ai
    SENDER_TYPES_SYSTEM             = 2 # Sent by athe system

class GenerationPresets:
    """
    Class containing various generation presets.
    """

    @staticmethod
    def deterministic_preset():
        """
        Preset for deterministic output with low temperature and top_k, and high top_p.
        """
        return {'temperature': 0.2, 'top_k': 10, 'top_p': 0.8}

    @staticmethod
    def creative_preset():
        """
        Preset for creative output with high temperature, top_k, and top_p.
        """
        return {'temperature': 0.8, 'top_k': 50, 'top_p': 0.9}

    @staticmethod
    def default_preset():
        """
        Default preset with moderate temperature, top_k, and top_p.
        """
        return {'temperature': 0.5, 'top_k': 20, 'top_p': 0.85}

class BindingType(Enum):
    """Binding types."""
    
    TEXT_ONLY = 0
    """This binding only supports text."""
    
    TEXT_IMAGE = 1
    """This binding supports text and image."""

    TEXT_IMAGE_VIDEO = 2
    """This binding supports text, image and video."""

    TEXT_AUDIO = 3
    """This binding supports text and audio."""

class SUMMARY_MODE(Enum):
    SUMMARY_MODE_SEQUENCIAL        = 0
    SUMMARY_MODE_HIERARCHICAL      = 0