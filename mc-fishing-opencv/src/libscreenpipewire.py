
import asyncio

from portal_screencast import PortalScreenCast
from libpipewire import PipeWireRecorder

from logs import logger

class ScreenCaptureApp:
    def __init__(self):
        self.portal = PortalScreenCast()
        self.recorder = PipeWireRecorder()
        self.frame_count = 0
        
    def on_state(self, old, new):
        logger.debug(f"🔄 [PipeWire] 状态: {old} → {new}")
        
    def on_format(self, w, h, fmt):
        logger.debug(f"📐 [PipeWire] 协商格式: {w}x{h}, fmt={fmt}")
        
    def on_frame(self, img_bgr, w, h):
        """处理每一帧 (业务逻辑：保存图片)"""
        self.frame_count += 1
        filename = f"frame_{self.frame_count:04d}.png"


    async def run(self):
        # 1. 请求 Portal 授权
        logger.debug("🔹 [Portal] 正在请求屏幕共享授权...")
        try:
            node_id = await self.portal.start()
        except Exception as e:
            logger.debug(f"❌ Portal 授权失败: {e}")
            return
        
        logger.debug(f"✅ [Portal] 授权成功! Node ID: {node_id}")
        
        # 2. 配置并启动 PipeWire
        self.recorder.set_callbacks(
            on_state=self.on_state,
            on_format=self.on_format,
            on_frame=self.on_frame
        )
        
        logger.debug("\n" + "="*50)
        logger.debug("🎥 录制中... (按 Ctrl+C 停止)")
        logger.debug("="*50 + "\n")
        
        pw_thread = self.recorder.start(node_id)
        
        # 3. 主线程在此等待停止信号
        try:
            while not self.recorder.stop_event.is_set():
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
            
        # 4. 清理资源
        logger.debug("🛑 [PipeWire] 正在停止...")
        self.recorder.stop()
        if pw_thread.is_alive():
            pw_thread.join(timeout=2.0)
            
        await self.portal.stop()
        logger.debug("🧹 所有资源已清理，再见！")
