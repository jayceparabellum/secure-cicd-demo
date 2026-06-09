from fastapi import FastAPI

app = FastAPI(title="Secure CI/CD Demo")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Secure CI/CD demo is running."}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
