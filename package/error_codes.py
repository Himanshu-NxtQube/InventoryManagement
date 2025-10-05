from enum import Enum

class ErrorCodes(Enum):
    # Rack related errors
    LEFT_BLUE_BAR_NOT_DETECTED = 101
    RIGHT_BLUE_BAR_NOT_DETECTED = 102
    UPPER_ORANGE_BAR_NOT_DETECTED = 103
    LOWER_ORANGE_BAR_NOT_DETECTED = 104

    # Rack ID related errors
    RACK_ID_NOT_ADJACENT = 201
    NO_RACK_ID_FOUND = 202
    WRONG_RACK_ID_ANNOTATION = 203

    # Unique ID related errors
    UNIQUE_ID_LOW_CONF_TYPE_1 = 301
    UNIQUE_ID_LOW_CONF_TYPE_2 = 302
    REPLACED_AT_SIGN = 303

    # Box/pallet detection errors
    ID_COUNT_MISMATCH = 401
    BACK_UNIQUE_ID_DETECTED = 402

    # Image related errors
    BLUR_IMAGE = 501
    LOW_IMAGE_RESOLUTION = 502
    LOW_LIGHT_IMAGE = 503

    # Sticker related errors
    STICKER_DAMAGE = 601
    STICKER_PARTIALLY_FOLD = 602
    STICKER_FOLDED_FROM_BOTTOM = 603