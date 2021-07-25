from ctypes import (CFUNCTYPE, POINTER, byref, c_uint16, c_void_p, cast,
                    create_string_buffer) # pylint: disable=unused-import
from threading import Lock

import numpy as np
from libuvc import (load_uvc, uv_context, uv_device, uv_device_handle,
                    uv_format_desc, uv_frame, uv_stream_control) # pylint: disable=unused-import

USB_VENDOR_ID = 0x1E4E
USB_PRODUCT_ID = 0x0100

VIDEO_STREAM_FORMAT_GUID_Y16 = create_string_buffer(
    b"Y16 \x00\x00\x10\x00\x80\x00\x00\xaa\x00\x38\x9b\x71", 16
)
UV_FRAME_FORMAT = 13


class frame_buffer(object):
    def initialize(self, width, height, dtype):
        self._shape = (height, width)
        self._buffers = [
            np.zeros(self._shape, dtype=dtype),
            np.zeros(self._shape, dtype=dtype),
        ]
        self._write_index = 0
        self._read_index = 1
        self._lock = Lock()

    def write(self, data):
        source = data.reshape(self._shape)
        destination = self._buffers[self._write_index]
        np.copyto(dst=destination, src=source)

    def read(self):
        assert self._lock.locked()
        return self._buffers[self._read_index]

    def read_lock(self):
        return self._lock

    def swap_buffers(self):
        with self._lock:
            self._write_index, self._read_index = (self._read_index, self._write_index)


libuvc = load_uvc()

frame_buffer = frame_buffer()


def uv_frame_callback(function):
    return CFUNCTYPE(None, POINTER(uv_frame), c_void_p)(function)


@uv_frame_callback
def frame_callback(frame_ptr, user_ptr):
    frame = frame_ptr.contents
    width = frame.width
    height = frame.height

    # write data from the callback into the frame buffer
    assert frame.data_bytes == 2 * width * height
    data_ptr = cast(frame.data, POINTER(c_uint16 * width * height))
    data = np.frombuffer(data_ptr.contents, dtype=np.uint16).reshape(height, width)
    frame_buffer.write(data)


class pure_thermal(object):
    def __init__(self):
        self._uv_context = POINTER(uv_context)()
        self._uv_device = POINTER(uv_device)()
        self._uv_device_handler = POINTER(uv_device_handle)()
        self._uv_stream_control = POINTER(uv_stream_control)()

        uvc_error = libuvc.uv_init(byref(self._uv_context), 0)
        if uvc_error < 0:
            raise RuntimeError("Failed to initialize uv context (error %d)" % uvc_error)

        uvc_error = libuvc.uv_open(self._uv_device, byref(self._uv_device_handler))
        if uvc_error < 0:
            raise RuntimeError("Failed to open uv device (error %d)" % uvc_error)

        frame_formats = self._frame_formats(VIDEO_STREAM_FORMAT_GUID_Y16)
        if not frame_formats:
            raise RuntimeError("Video stream format GUID Y16 not supported yet")

        frame_format = frame_formats[0]
        frame_format_fps = int(1e7 / frame_format.dwDefaultFrameInterval)
        uvc_error = libuvc.uv_get_stream_control_format_size(
            self._uv_device_handler,
            byref(self._uv_stream_control),
            UV_FRAME_FORMAT,
            frame_format.wWidth,
            frame_format.wHeight,
            frame_format_fps,
        )
        if uvc_error < 0:
            raise RuntimeError(
                "Failed to negotiate stream profile (error %d)" % uvc_error
            )

        self._frame_width = frame_format.wWidth
        self._frame_height = frame_format.wHeight
        frame_buffer.initialize(self._frame_width, self._frame_height, np.uint16)

        uvc_error = libuvc.uv_start_streaming(
            self._uv_device_handler,
            byref(self._uv_stream_control),
            frame_callback,
            None,
            0,
        )

        if uvc_error < 0:
            raise RuntimeError("Failed to streaming (error %d)" % uvc_error)

        return self

    def __exit__(self, type, value, traceback):
        libuvc.uv_stop_streaming(self._uv_device_handler)
        libuvc.uv_unref_device(self._uv_device)
        libuvc.uv_exit(self._uv_context)

    def frame(self):
        return frame_buffer.read()

    def frame_lock(self):
        return frame_buffer.read_lock()

    def width(self):
        return self._frame_width

    def height(self):
        return self._frame_height

    def _as_iterator(self, pointer):
        while pointer:
            contents = pointer.contents
            yield contents
            pointer = contents.next

    def _frame_formats(self, video_stream_format_guid):
        frame_formats = []

        libuvc.uvc_get_format_desc.restype = POINTER(uv_format_desc)
        format_desc_ptr = libuvc.uv_get_format_desc(self._uv_device_handler)
        for format_desc in self._as_iterator(format_desc_ptr):
            if format_desc.guidFormat[0:4] != video_stream_format_guid[0:4]:
                continue

            frame_desc_ptr = format_desc.frame_desc
            for frame_desc in self._as_iterator(frame_desc_ptr):
                frame_formats.append(frame_desc)

        return frame_formats
