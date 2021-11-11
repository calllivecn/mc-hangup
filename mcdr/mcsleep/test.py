
import os
import asyncio
import signal

PLUGIN_RELOAD = False

def handle_reload(arg1, arg2):
    print("handle_reload args:", arg1, arg2)
    global PLUGIN_RELOAD

    PLUGIN_RELOAD = True
    print("收到SIGHUP 信号，把 PLUGIN_RELOAD = True")

signal.signal(signal.SIGHUP, handle_reload)

def httpResponse(msg):
    msg = "<h1>" + msg + "</h1>\n"
    msg = msg.encode("utf8")
    response = [
            "HTTP/1.1 200 ok",
            "Server: server",
            "Content-Type: text/html;charset=UTF-8",
            "Content-Length: " + str(len(msg)), "\r\n",
            ]
    data = "\r\n".join(response).encode("utf8") + msg
    return data


async def return_ip(writer, ip):
    writer.write(httpResponse(ip))
    await writer.drain()

    writer.close()
    await writer.wait_closed()


async def handler(reader, writer):
    addr = writer.transport.get_extra_info("peername")
    print("client: ", addr)

    try:
        data = await asyncio.wait_for(reader.read(1024), timeout=5)
    except asyncio.exceptions.TimeoutError:
        await return_ip(writer, addr[0])
        return


    if data:

        try:
            content = data.decode()

            oneline = content.split("\r\n")[0]

            method, path, protocol = oneline.split(" ")
        except UnicodeDecodeError as e:
            print(e, addr)
            await return_ip(writer, addr[0])
            return

        except Exception as e:
            print("有异常:", e)
            # traceback.print_exc()
            await return_ip(writer, addr[0])
            return

        if path == "/123":
            # check_mc_server_is_running
            writer.write(httpResponse("未知状态..."))
            await writer.drain()

            writer.close()
            await writer.wait_closed()
        else:
            await return_ip(writer, addr[0])



async def recv_handler(r, w):
    try:
        await handler(r, w)
    except asyncio.exceptions.CancelledError:
        w.close()
        await w.wait_closed()

async def asyncio_check_exit(server):
    """
    检查插件是否重载, 是：退出些loop
    """

    while True:
        if PLUGIN_RELOAD:
            # server.logger.info("olg_plugin 执行器退出...")
            print("old_plugin 执行器退出...")

            # close server
            server.close()
            await server.wait_closed()

            # 清理还未执行完成的 task
            tasks = asyncio.all_tasks()
            tasks_len = len(tasks)
            print("asyncio.all_tasks() --> ", tasks_len)
            for task in tasks:
                task.cancel()
            break
        else:
            await asyncio.sleep(1)


async def httpmcsleep():
    server = await asyncio.start_server(recv_handler, "*", 8111, reuse_address=True, reuse_port=True)

    print("type(server): ", type(server))

    # 和 server 并行运行
    check = asyncio.create_task(asyncio_check_exit(server))
    await check

    async with server:
        await server.serve_forever()

    # 这个协程在前面被取消了，这里执行不到
    print("htptmcsleep() exit")


def start_httpmcsleep():
    print("pid: ", os.getpid())

    try:
        asyncio.run(httpmcsleep())
    except asyncio.exceptions.CancelledError:
        print("start_httpmcslee() CancelledError")


    #  在这之后，应该没有还在执行loop了吧. 对没有了， 所有task都取消了。
    try:
        loop = asyncio.get_running_loop()
    except Exception:
        print("asyncio.run() 之后没有loop了.~")

    print("all done exit")


start_httpmcsleep()