from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommender.llm_preprocess import extract_structured
from recommender.recommend import Recommender
import uvicorn

app = FastAPI(title='SHL Assessment Recommender')

class Query(BaseModel):
    query: str
    max_results: int = 10

recommender = Recommender()

@app.get('/health')
def health():
    return {'status':'ok'}

@app.post('/recommend')
def recommend(q: Query):
    try:
        structured = extract_structured(q.query)
        results = recommender.balanced_recommend(structured, k=q.max_results)
        if len(results) < 1:
            raise HTTPException(status_code=404, detail='No recommendations found')
        response = {'query': q.query, 'recommendations': [{'assessment_name': r['assessment_name'], 'assessment_url': r['assessment_url']} for r in results]}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
