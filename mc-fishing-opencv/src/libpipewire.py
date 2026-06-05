import threading

import numpy as np

from _pipewire_cffi import ffi, lib

class PipeWireRecorder:
    """
    PipeWire 屏幕录制器封装库。
    负责 C 层生命周期管理、FPS 限制、区域裁剪以及帧数据分发。
    """
    def __init__(self):
        self.pw_ctx = None
        self.is_streaming = False
        self._c_refs = []  # 防止 CFFI 回调被 GC 回收
        
        # 线程同步信号
        self.stop_event = threading.Event()
        
        # 用户回调
        self._user_on_state = None
        self._user_on_format = None
        self._user_on_frame = None
        
        # 配置参数
        self.target_fps = 30
        self.enable_crop = False
        self.crop_x, self.crop_y, self.crop_w, self.crop_h = 0, 0, 0, 0

    def set_crop_region(self, x: int, y: int, w: int, h: int):
        """设置 C 层高性能裁剪区域"""
        self.crop_x = x
        self.crop_y = y
        self.crop_w = w
        self.crop_h = h
        self.enable_crop = True

    def disable_crop(self):
        """禁用裁剪"""
        self.enable_crop = False

    def set_target_fps(self, fps: int):
        """设置目标 FPS"""
        self.target_fps = max(1, fps)

    def set_callbacks(self, on_state=None, on_format=None, on_frame=None):
        """
        注册外部回调。
        on_state:  fn(old_state: str, new_state: str)
        on_format: fn(width: int, height: int, fmt: int)
        on_frame:  fn(img_bgr: np.ndarray, width: int, height: int)
        """
        self._user_on_state = on_state
        self._user_on_format = on_format
        self._user_on_frame = on_frame

    def _setup_pw_callbacks(self):
        """绑定 C 层回调到 Python"""
        @ffi.callback("void(void*, int, int)")
        def _on_state(userdata, old, new):
            states = ["UNCONNECTED", "CONNECTING", "PAUSED", "STREAMING", "ERROR"]
            old_str = states[old] if 0 <= old < len(states) else f"UNKNOWN({old})"
            new_str = states[new] if 0 <= new < len(states) else f"UNKNOWN({new})"
            
            if new == 3:  # STREAMING
                self.is_streaming = True
            elif new == 4:  # ERROR
                self.stop_event.set()
                
            if self._user_on_state:
                self._user_on_state(old_str, new_str)

        @ffi.callback("void(void*, uint32_t, uint32_t, uint32_t)")
        def _on_format(userdata, w, h, fmt):
            if self._user_on_format:
                self._user_on_format(w, h, fmt)

        @ffi.callback("void(void*, void*, uint32_t, uint32_t, uint32_t, uint32_t)")
        def _on_frame(userdata, data_ptr, size, w, h, stride):
            if not self.is_streaming:
                return
            
            try:
                # 1. 零拷贝获取内存视图
                raw_bytes = np.frombuffer(ffi.buffer(data_ptr, size), dtype=np.uint8)
                
                # 2. 重塑数组 (处理 stride 内存对齐)
                if stride == w * 4:
                    img_array = raw_bytes.reshape((h, w, 4))
                else:
                    img_array = raw_bytes.reshape((h, stride // 4, 4))[:, :w, :]
                    
                # 3. 颜色空间转换 (BGRx -> BGR)
                img_bgr = img_array[:, :, :3].copy() # .copy() 确保内存连续，方便后续 OpenCV 处理
                
                # 4. 触发用户回调
                if self._user_on_frame:
                    self._user_on_frame(img_bgr, w, h)
                    
            except Exception as e:
                print(f"❌ [PipeWire] 帧处理异常: {e}")

        # 保持回调引用
        self._c_refs.extend([_on_state, _on_format, _on_frame])
        lib.set_callbacks(self.pw_ctx, ffi.NULL, _on_state, _on_format, _on_frame)

    def start(self, node_id: int):
        """在后台线程中启动 PipeWire"""
        self.pw_ctx = lib.create_recorder()
        if not self.pw_ctx:
            raise RuntimeError("创建 PipeWire 上下文失败！")
        
        self._setup_pw_callbacks()
        
        # 配置 C 层参数
        lib.set_target_fps(self.pw_ctx, self.target_fps)
        if self.enable_crop:
            lib.set_crop_region(self.pw_ctx, 1, self.crop_x, self.crop_y, self.crop_w, self.crop_h)
        else:
            lib.set_crop_region(self.pw_ctx, 0, 0, 0, 0, 0)
            
        if lib.connect_stream(self.pw_ctx, node_id) < 0:
            lib.destroy_recorder(self.pw_ctx)
            raise RuntimeError("连接 PipeWire 流失败！")
            
        pw_thread = threading.Thread(target=self._run_loop, daemon=True)
        pw_thread.start()
        return pw_thread

    def _run_loop(self):
        try:
            lib.run_loop(self.pw_ctx)
        except Exception as e:
            print(f"💥 PipeWire 线程异常: {e}")
        finally:
            self.stop_event.set()

    def stop(self):
        """停止并清理 PipeWire 资源"""
        if self.pw_ctx:
            lib.stop_loop(self.pw_ctx)
            lib.destroy_recorder(self.pw_ctx)
            self.pw_ctx = None
