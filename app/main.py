# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn # Needed if running via python main.py

app = FastAPI(title="Vue-FastAPI Cropping Demo")

# 1. Mount the 'static' directory
# This makes everything inside the 'static' folder accessible via the /static URL path.
# For example, app.js will be available at http://localhost:8000/static/js/app.js
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Define the root route ("/")
@app.get("/", response_class=HTMLResponse)
async def serve_vue_app():
    """Serves the index.html page."""
    try:
        # --- FIX: Explicitly specify encoding as 'utf-8' ---
        with open("static/index.html", "r", encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found in the 'static' directory.</h1>", status_code=404)
# (Include your API endpoints here: /api/submit_image/ and /api/submit_cropped_data/)
# ...

# Optional: Run command if executing main.py directly
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)