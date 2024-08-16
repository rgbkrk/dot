## Dot

Dot is an initial implementation of the Context Server Protocol (CSP) for use with Zed.

### Install

```bash
pip install dot
```


### Example

```python
from pydantic import Field

from dot import txt, context_server
import asyncio

@txt
async def echo(text: str = Field(..., description="text to repeat back")):
    return text

if __name__ == "__main__":
    asyncio.run(context_server.run())
```
