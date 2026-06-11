"""Portal ScreenCast 异步模块 (保持会话存活)"""
import asyncio


from dbus_next.aio.message_bus import MessageBus
from dbus_next import Message
from dbus_next.signature import Variant
from dbus_next.constants import MessageType, BusType


class PortalScreenCast:
    def __init__(self):
        self.bus = None
        self.sender = None
        self.session_handle = None
        self.node_id = None
        self._token_counter = 0

    def _get_unique_token(self):
        self._token_counter += 1
        return f"pytoken{self._token_counter}"

    async def _call_and_wait(self, method, signature, body):
        token = self._get_unique_token()
        expected_path = f"/org/freedesktop/portal/desktop/request/{self.sender}/{token}"
        
        if isinstance(body[-1], dict):
            body[-1]['handle_token'] = Variant('s', token)
            
        response_event = asyncio.Event()
        response_data = {}
        
        def signal_handler(msg):
            if msg.message_type != MessageType.SIGNAL:
                return False
            if (msg.interface == 'org.freedesktop.portal.Request' and msg.member == 'Response' and msg.path == expected_path):
                response_code = msg.body[0]
                if response_code == 0:
                    response_data.update({k: v.value for k, v in msg.body[1].items()})
                else:
                    response_data['error'] = response_code
                response_event.set()
                return False
                
        self.bus.add_message_handler(signal_handler)
        try:
            msg = Message(
                destination='org.freedesktop.portal.Desktop',
                path='/org/freedesktop/portal/desktop',
                interface='org.freedesktop.portal.ScreenCast',
                member=method,
                signature=signature,
                body=body
            )
            reply = await self.bus.call(msg)
            if reply.message_type == MessageType.ERROR:
                raise RuntimeError(f"D-Bus 错误: {reply.error_name}")
                
            await asyncio.wait_for(response_event.wait(), timeout=120.0)
            if 'error' in response_data:
                raise RuntimeError(f"Portal 拒绝授权 (Code: {response_data['error']})")
            return response_data
        finally:
            self.bus.remove_message_handler(signal_handler)

    async def start(self):
        """发起屏幕共享请求并阻塞等待用户授权，返回 Node ID"""
        print("🔹 [Portal] 连接 D-Bus 会话总线...")
        self.bus = await MessageBus(bus_type=BusType.SESSION).connect()
        self.sender = self.bus.unique_name.replace('.', '_').replace(':', '_')[1:]
        
        print("🔹 [Portal] 1/3 创建会话...")
        session_token = f"pysession{self._token_counter}"
        res = await self._call_and_wait('CreateSession', 'a{sv}', [{'session_handle_token': Variant('s', session_token)}])
        self.session_handle = res['session_handle']
        
        print("🔹 [Portal] 2/3 选择捕获源 (窗口)...")

        await self._call_and_wait('SelectSources', 'oa{sv}', [
            self.session_handle,
            {'types': Variant('u', 1), 'cursor_mode': Variant('u', 1), 'multiple': Variant('b', False)}
        ])
        
        print("🔹 [Portal] 3/3 启动捕获 (请在弹窗中选择窗口并点击共享)...")
        res = await self._call_and_wait('Start', 'osa{sv}', [self.session_handle, "", {}])
        streams = res.get('streams', [])
        if not streams:
            raise RuntimeError("未获取到视频流")
            
        self.node_id = int(streams[0][0])
        print(f"✅ [Portal] 授权成功! 保持会话存活中... (Node ID: {self.node_id})")
        return self.node_id

    async def stop(self):
        """优雅关闭 Portal 会话"""
        if self.session_handle and self.bus:
            print("🧹 [Portal] 正在关闭屏幕共享会话...")
            try:
                msg = Message(
                    destination='org.freedesktop.portal.Desktop',
                    path=self.session_handle,
                    interface='org.freedesktop.portal.Session',
                    member='Close',
                    signature=''
                )
                await self.bus.call(msg)
            except Exception:
                pass
        if self.bus:
            self.bus.disconnect()
