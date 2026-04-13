"""
CASA Gateway
  /landingpage  → landing.html (static)
  /             → redirect to /landingpage
  everything else → proxy to Streamlit (internal port 8502)
"""
import asyncio, os
import httpx
import aiohttp
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, Response, RedirectResponse
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.websockets import WebSocket

STREAMLIT_PORT = int(os.environ.get("STREAMLIT_PORT", 8502))
GATEWAY_PORT   = int(os.environ.get("GATEWAY_PORT",   8501))
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))


# ── Landing page ──────────────────────────────────────────────
async def landing(request: Request):
    return FileResponse(os.path.join(BASE_DIR, "landing.html"))

async def root_redirect(request: Request):
    return RedirectResponse(url="/landingpage", status_code=302)

async def app_redirect(request: Request):
    """Redirect /app and /app/* to the landing page."""
    return RedirectResponse(url="/landingpage", status_code=302)


# ── HTTP proxy → Streamlit ─────────────────────────────────────
async def proxy_http(request: Request):
    path  = request.url.path
    query = f"?{request.url.query}" if request.url.query else ""
    target = f"http://localhost:{STREAMLIT_PORT}{path}{query}"

    skip_req = {"host", "connection", "keep-alive", "te", "trailers",
                "transfer-encoding", "upgrade"}
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in skip_req}

    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        try:
            resp = await client.request(
                method  = request.method,
                url     = target,
                headers = headers,
                content = await request.body(),
            )
            skip_resp = {"content-encoding", "transfer-encoding", "content-length",
                         "connection", "keep-alive", "te", "trailers", "upgrade"}
            fwd_headers = {k: v for k, v in resp.headers.items()
                           if k.lower() not in skip_resp}
            return Response(
                content     = resp.content,
                status_code = resp.status_code,
                headers     = fwd_headers,
            )
        except httpx.ConnectError:
            return Response("Streamlit not reachable — is it running?", status_code=502)
        except Exception as e:
            return Response(f"Proxy error: {e}", status_code=502)


# ── WebSocket proxy → Streamlit ────────────────────────────────
async def proxy_ws(websocket: WebSocket):
    subprotocols = websocket.scope.get("subprotocols", [])
    await websocket.accept(subprotocol=subprotocols[0] if subprotocols else None)

    path  = websocket.url.path
    query = f"?{websocket.url.query}" if websocket.url.query else ""
    target = f"ws://localhost:{STREAMLIT_PORT}{path}{query}"

    try:
        session = aiohttp.ClientSession()
        try:
            upstream = await session.ws_connect(
                target,
                headers={"origin": f"http://localhost:{STREAMLIT_PORT}"},
                protocols=subprotocols if subprotocols else None,
                max_msg_size=0,
                autoclose=False,
                autoping=True,
            )
        except Exception:
            await websocket.close()
            await session.close()
            return

        async def fwd_up():
            try:
                while True:
                    msg = await websocket.receive()
                    if msg["type"] == "websocket.disconnect":
                        break
                    if msg.get("bytes"):
                        await upstream.send_bytes(msg["bytes"])
                    elif msg.get("text"):
                        await upstream.send_str(msg["text"])
            except Exception:
                pass
            finally:
                await upstream.close()

        async def fwd_dn():
            try:
                async for msg in upstream:
                    if msg.type == aiohttp.WSMsgType.BINARY:
                        await websocket.send_bytes(msg.data)
                    elif msg.type == aiohttp.WSMsgType.TEXT:
                        await websocket.send_text(msg.data)
                    elif msg.type in (aiohttp.WSMsgType.CLOSED,
                                      aiohttp.WSMsgType.ERROR):
                        break
            except Exception:
                pass

        tasks = [asyncio.create_task(fwd_up()),
                 asyncio.create_task(fwd_dn())]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

        await upstream.close()
        await session.close()

    except Exception:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


# ── Routes ─────────────────────────────────────────────────────
# WebSocket paths (no baseUrlPath — Streamlit uses /_stcore/stream)
WS_PATHS = ["/_stcore/stream", "/stream"]

routes = [
    Route("/",                root_redirect),
    Route("/landingpage",     landing),
    Route("/landing.html",    landing),
    Route("/app",             app_redirect),
    Route("/app/{rest:path}", app_redirect),
    *[WebSocketRoute(p, proxy_ws) for p in WS_PATHS],
    Route("/{rest:path}",     proxy_http),
]

app = Starlette(routes=routes)


if __name__ == "__main__":
    import uvicorn
    print(f"\n  CASA Gateway  (port {GATEWAY_PORT})")
    print(f"  Landing : http://localhost:{GATEWAY_PORT}/landingpage")
    print(f"  App     : http://localhost:{GATEWAY_PORT}/")
    print(f"  → Streamlit runs internally on port {STREAMLIT_PORT}\n")
    uvicorn.run(app, host="0.0.0.0", port=GATEWAY_PORT, log_level="warning")
