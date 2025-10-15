from fastapi import FastAPI
from pydantic import BaseModel
from website_bot import scrape_site

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
    uvicorn.run("api:app", host="0.0.0.0", port=10000)
