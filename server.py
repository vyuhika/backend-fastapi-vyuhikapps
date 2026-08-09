from fastapi import FastAPI

app = FastAPI()



# Server Health Check Endpoint
@app.get('/health')
def health_status_check():
    return {
        'status': 'ONLINE',
        'errors': {
            'msg': '',
        },
    }





if __name__ == "__main__":

    import uvicorn
    
    uvicorn.run(app)
