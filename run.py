import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from re import fullmatch


app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.get('/', response_class=RedirectResponse)
async def index(request: Request):
    return RedirectResponse('https://github.com/SkylaDev/scratch-embed-fixer', status_code=308)


@app.get('/{project_id}', response_class=HTMLResponse)
@app.get('/projects/{project_id}', response_class=HTMLResponse)
async def embed_project(request: Request, project_id: str):
    if not fullmatch(r'\d+', project_id):
        raise HTTPException(status_code=404, detail='Invalid project ID')
    
    try:
        async with httpx.AsyncClient(follow_redirects=False, timeout=5) as session:
            resp = await session.get(('https://api.scratch.mit.edu/projects/%s' % project_id),
                                     headers={'User-Agent': 'ScratchEmbedFixer/1.0'})
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail='Scratch API timeout')
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail='Unable to connect to Scratch API')
    except:
        raise HTTPException(status_code=500)
    
    if resp.status_code == 404: raise HTTPException(status_code=404, detail='Invalid project ID')
    if resp.status_code != 200: raise HTTPException(status_code=502, detail='Scratch API error')
    
    data = resp.json()
    
    return templates.TemplateResponse(request=request, name='project.html',
                                      context={'project_id': project_id,
                                               'title': data.get('title', None) or ('Scratch project #%s' % project_id),
                                               'description': data.get('description', None) or 'View this project on Scratch!',
                                               'author': data.get('author', {}).get('username', '') or 'Scratch User',
                                               'thumbnail': data.get('image', None) or ('https://uploads.scratch.mit.edu/get_image/project/%s_480x360.png' % project_id) # Found this manual method also works as a fallback
                                               })
