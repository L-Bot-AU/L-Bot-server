import websockets
import asyncio
import json
async def server(websocket, path):
  print(websocket, path)
  options = {
        "/snrCount": lambda: '23',#str(count("snr")),
        "/jnrCount": lambda: '59',#str(count("jnr")),
        "/snrTime": lambda: '"break 1"',
        "/jnrTime": lambda: '"break 1"',
        "/jnrPredictions": lambda: '''{"labels": ["Morning", "Break 1", "Break 2"],
"data": [[53, 34, 26],
[52, 54, 20],
[44, 14, 30],
[40, 12, 12],
[80, 14, 33]
]
}''',
        "/snrPredictions": lambda: '''{"labels": ["Morning", "Break 1", "Break 2"],
"data": [[53, 34, 26],
[52, 54, 20],
[44, 14, 30],
[40, 12, 12],
[80, 14, 33]
]
}'''
  }

  await websocket.send(options.get(path, lambda : "Could not recognise action")())
start_server = websockets.serve(server, "127.0.0.1", 2910)
print("Server open")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
