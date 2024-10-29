from fastapi import FastAPI
from core.database import Base
from core.database import engine
from api.userModule.userAPI import user_router
from api.userModule.roleAPI import role_router
from api.articleModule.categoryAPI import category_router
from api.articleModule.articleAPI import article_router
from api.notificationModule.notificationAPI import notification_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["http://127.0.0.1:3000", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # Specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(user_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(article_router, prefix="/api/v1")
app.include_router(notification_router, prefix="/api/v1")


# @app.on_event("startup")
# def startup_event():
#     Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Message": "Welcome to this basic appss"}





# command for 
    #  installing all from requirements.txt: 
            #  pip install -r requirements.txt
    # settign up venv:  python -m venv venv
    # activate venv: .\venv\Scripts\activate
    # deactivate venv: deactivate
    # see all inatalled libraries: pip list"
    # run uvicorn server: uvicorn main:app --reload --port 8080

