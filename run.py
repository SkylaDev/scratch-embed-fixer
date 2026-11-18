import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from re import fullmatch


app = FastAPI(docs_url=None, openapi_url=None, redoc_url=None)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


async def api_request(endpoint: str, *args, **kwargs) -> dict:
    """Simple function to make API requests to the Scratch API and handle error codes.

    Args:
        endpoint (str): API endpoint to get from.

    Raises:
        HTTPException: Any error that is caught from the request, raised back to the client.

    Returns:
        dict: Response from Scratch API in JSON format.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=False, timeout=5) as session:
            resp = await session.get('https://api.scratch.mit.edu' + endpoint,
                                     headers={'User-Agent': 'ScratchEmbedFixer/1.1'},
                                     *args, **kwargs)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail='Scratch API timeout')
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail='Unable to connect to Scratch API')
    except:
        raise HTTPException(status_code=500)

    if resp.status_code == 404: raise HTTPException(status_code=404)
    if resp.status_code != 200: raise HTTPException(status_code=502, detail='Scratch API error')
        
    return resp.json()


@app.get('/', response_class=RedirectResponse)
async def index(request: Request):
    return RedirectResponse('https://github.com/SkylaDev/scratch-embed-fixer', status_code=308)


@app.get('/{project_id}', response_class=HTMLResponse)
@app.get('/project/{project_id}', response_class=HTMLResponse)
@app.get('/projects/{project_id}', response_class=HTMLResponse)
async def embed_project(request: Request, project_id: str):
    if not fullmatch(r'\d+', project_id):
        raise HTTPException(status_code=404, detail='Invalid project ID')
    
    data = await api_request('/projects/%s' % project_id)
    
    return templates.TemplateResponse(request=request, name='project.html',
                                      context={'project_id': project_id,
                                               'title': data.get('title', None) or ('Scratch project #%s' % project_id),
                                               'description': data.get('description', None) or 'View this project on Scratch!',
                                               'author': data.get('author', {}).get('username', '') or 'Scratch User',
                                               # Found this manual method also works as a fallback
                                               'thumbnail': data.get('image', None) or ('https://uploads.scratch.mit.edu/get_image/project/%s_480x360.png' % project_id)})


@app.get('/studio/{studio_id}', response_class=HTMLResponse)
@app.get('/studios/{studio_id}', response_class=HTMLResponse)
async def embed_studio(request: Request, studio_id: str):
    if not fullmatch(r'\d+', studio_id):
        raise HTTPException(status_code=404, detail='Invalid studio ID')
        
    data = await api_request('/studios/%s' % studio_id)
    
    return templates.TemplateResponse(request=request, name='studio.html',
                                      context={'studio_id': studio_id,
                                               'title': data.get('title', None) or ('Scratch studio #%s' % studio_id),
                                               'description': data.get('description', None) or 'View this studio on Scratch!',
                                               # Like with projects, if the image fails to be returned, use the usual URL format as a fallback
                                               'thumbnail': data.get('image', None) or ('https://uploads.scratch.mit.edu/get_image/gallery/%s_170x100.png' % studio_id)})


@app.get('/user/{username}', response_class=HTMLResponse)
@app.get('/users/{username}', response_class=HTMLResponse)
async def embed_user(request: Request, username: str):
    if not fullmatch(r'^[A-Za-z0-9_-]{3,20}$', username):
        raise HTTPException(status_code=404, detail='Invalid username')
    
    data = await api_request('/users/%s' % username)
    profile: dict = data.get('profile', {})
    
    return templates.TemplateResponse(request=request, name='user.html',
                                      context={'username': username,
                                               'bio': profile.get('bio', ''),
                                               # Best to use this as the API only returns up to a 90x90 avatar
                                               'avatar': 'https://uploads.scratch.mit.edu/get_image/user/%s_256x256.png' % data.get('id', '')})
