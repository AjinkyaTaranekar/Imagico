import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app", workers=1, loop="asyncio", host="0.0.0.0", port=8080, reload=True
    )
