from fastapi import FastAPI


from app.core.config import settings
from app.api.router import api_router


app = FastAPI(
    title= settings.app_name,
    version= settings.app_version,
    description= "Apps for vyuhika platform.",
)

app.include_router(
    api_router,
    prefix= "/api/v1",
)



# Server Health Check Endpoint
@app.get('/health', tags=["Health"])
async def health_status_check():
    return {
        'status': 'ONLINE',
        'environment': settings.app_env,
        'errors': {
            'msg': '',
        },
    }



if __name__ == "__main__":

    import uvicorn
    
    uvicorn.run(app)
