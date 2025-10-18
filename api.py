from fastapi import FastAPI
from website_bot import scrape_site
from pydantic import BaseModel
import os

app = FastAPI(
    title="AI Agents API Collection",
    description="Dheeraj",
    version="1.0",
    docs_url="/ai-agents/docs",
    redoc_url="/ai-agents/redoc"
)

@app.get("/")
def root():
    return {
        "message": "API is live. Use POST /scrape with JSON body {'url': 'yourwebsite.com'}"
    }

class UrlInput(BaseModel):
    url: str

@app.post("/scrape")
def scrape_data(input_data: UrlInput):
    if not input_data.url.strip():
        return {"message": "URL is required"}
    try:
        data = scrape_site(input_data.url)
        return {"message": "Scraping complete", "data": data}
    except Exception as e:
        return {"message": "Error occurred during scraping", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Railway provides PORT dynamically
    uvicorn.run("api:app", host="0.0.0.0", port=port)
