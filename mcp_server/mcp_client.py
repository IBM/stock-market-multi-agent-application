from mcp import ClientSession
from mcp.client.sse import sse_client

class MCPClient:
    async def connect_to_sse_server(self, url):
        self.stream_context = sse_client(url = url)
        streams = await self.stream_context.__aenter__()
        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()
        await self.session.initialize()
    
    async def cleanup(self):
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
            if self.stream_context:
                await self.stream_context.__aexit__(None, None, None)
        except Exception as e:
            print(f"Error closing connection : {e}")