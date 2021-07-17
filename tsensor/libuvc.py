from ctypes import CDLL
from ctypes import Structure
from ctypes import c_int
from ctypes import CFUNCTYPE
from ctypes import POINTER
from ctypes import c_char
from ctypes import c_long
from ctypes import c_size_t
from ctypes import c_ubyte
from ctypes import c_uint
from ctypes import c_uint16
from ctypes import c_uint32
from ctypes import c_uint8
from ctypes import c_ulong
from ctypes import c_void_p


def load_uvc():
    return CDLL("libuvc.so")


class uv_context(Structure):
    _fields_ = [
        ("usb_ctx", c_void_p),
        ("own_usb_ctx", c_uint8),
        ("open_devices", c_void_p),
        ("handler_thread", c_ulong),
        ("kill_handler_thread", c_int),
    ]


class uv_device(Structure):
    _fields_ = [("ctx", POINTER(uv_context)), ("ref", c_int), ("usb_dev", c_void_p)]


class uv_device_handle(Structure):
    _fields_ = [
        ("dev", POINTER(uv_device)),
        ("prev", c_void_p),
        ("next", c_void_p),
        ("usb_devh", c_void_p),
        ("info", c_void_p),
        ("status_xfer", c_void_p),
        ("status_buf", c_ubyte * 32),
        ("status_cv", c_void_p),
        ("status_user_ptr", c_void_p),
        ("button_cb", c_void_p),
        ("button_user_ptr", c_void_p),
        ("streams", c_void_p),
        ("is_isight", c_ubyte),
    ]


class uv_stream_control(Structure):
    _fields_ = [
        ("bmHint", c_uint16),
        ("bFormatIndex", c_uint8),
        ("bFrameIndex", c_uint8),
        ("dwFrameInterval", c_uint32),
        ("wKeyFrameRate", c_uint16),
        ("wPFrameRate", c_uint16),
        ("wCompQuality", c_uint16),
        ("wCompWindowSize", c_uint16),
        ("wDelay", c_uint16),
        ("dwMaxVideoFrameSize", c_uint32),
        ("dwMaxPayloadTransferSize", c_uint32),
        ("dwClockFrequency", c_uint32),
        ("bmFramingInfo", c_uint8),
        ("bPreferredVersion", c_uint8),
        ("bMinVersion", c_uint8),
        ("bMaxVersion", c_uint8),
        ("bInterfaceNumber", c_uint8),
    ]


class uv_frame_desc(Structure):
    pass


class uv_format_desc(Structure):
    pass


uv_frame_desc._fields_ = [
    ("parent", POINTER(uv_format_desc)),
    ("prev", POINTER(uv_frame_desc)),
    ("next", POINTER(uv_frame_desc)),
    ("bDescriptorSubtype", c_uint),
    ("bFrameIndex", c_uint8),
    ("bmCapabilities", c_uint8),
    ("wWidth", c_uint16),
    ("wHeight", c_uint16),
    ("dwMinBitRate", c_uint32),
    ("dwMaxBitRate", c_uint32),
    ("dwMaxVideoFrameBufferSize", c_uint32),
    ("dwDefaultFrameInterval", c_uint32),
    ("dwMinFrameInterval", c_uint32),
    ("dwMaxFrameInterval", c_uint32),
    ("dwFrameIntervalStep", c_uint32),
    ("bFrameIntervalType", c_uint8),
    ("dwBytesPerLine", c_uint32),
    ("intervals", POINTER(c_uint32)),
]

uv_format_desc._felds_ = [
    ("parent", c_void_p),
    ("prev", POINTER(uv_format_desc)),
    ("next", POINTER(uv_format_desc)),
    ("bDescriptorSubtype", c_uint),
    ("bFormatIndex", c_uint8),
    ("bNumFrameDescriptors", c_uint8),
    ("guidFormat", c_char * 16),
    ("bBitsPerPixel", c_uint8),
    ("bDefaultFrameIndex", c_uint8),
    ("bAspectRatioX", c_uint8),
    ("bAspectRatioY", c_uint8),
    ("bmInterlaceFlags", c_uint8),
    ("bCopyProtect", c_uint8),
    ("bVariableSize", c_uint8),
    ("frame_descs", POINTER(uv_frame_desc)),
]


class time_val(Structure):
    _fields_ = [("tv_sec", c_long), ("tv_usec", c_long)]


class uv_frame(Structure):
    _fields_ = [
        ("data", POINTER(c_uint8)),
        ("data-bytes", c_size_t),
        ("width", c_uint32),
        ("height", c_uint32),
        ("frame_format", c_uint),
        ("step", c_size_t),
        ("sequence", time_val),
        ("source", POINTER(uv_device)),
        ("library_owns_data", c_uint8),
    ]
