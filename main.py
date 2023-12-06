from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Form, Query, Path, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from api.user import *
from api.mini_program_name import *
from api.mini_program_package import *
from api.mini_program import *
from api.blue_device import *
from tools.tools import *
from pydantic import BaseModel
from typing import List


class ProgramItem(BaseModel):
    uuid: str
    icon: str
    device_uuid: str
    names: List[dict]


app = FastAPI()
config = read_config()
Base = declarative_base()

DATABASE_URL = f"mysql+mysqlconnector://{config.get('mysql', 'user')}:{config.get('mysql', 'password')}@{config.get('mysql', 'host')}/{config.get('mysql', 'database')}"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
session_factory = sessionmaker(autocommit=False,
                               autoflush=False,
                               bind=engine)


def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = config.get('token', 'SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


def create_access_token(data: dict,
                        expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 验证密码
def verify_password(plain_password,
                    hashed_password):
    return genarate_passwd(plain_password) == hashed_password


@app.get("/current_user")
async def get_current_user_route(current_user: dict = Depends(get_current_user)):
    return current_user


# Login endpoint
@app.post("/user/login/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if user is None or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Create an access token that expires in 30 minutes
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": f"Bearer {access_token}"}


@app.post("/user/register/")
async def add_user(username: str = Form(...),
                   password: str = Form(...),
                   db: Session = Depends(get_db)):
    try:
        create_user(db, username, genarate_passwd(password))
        return {'detail': {"message": "success"}}
    except Exception as e:
        if '(mysql.connector.errors.IntegrityError) 1062 (23000): Duplicate entry' in str(e):
            raise HTTPException(status_code=400,
                                detail={"message": f"Duplicate entry '{username}' for key 'user.username'"})
        else:
            raise HTTPException(status_code=400, detail="error")


@app.get("/program/detail/")
async def get_program_detail(token: str = Depends(oauth2_scheme),
                             state: str = Query(..., description="A required parameter"),
                             uuid: str = Query(None, description="Optional. Provide either uuid or device_uuid."),
                             device_uuid: str = Query(None, description="Optional. Provide either uuid or device_uuid."),
                             db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Successful verification
        if not state:
            raise HTTPException(status_code=400, detail="State is required")
        if not uuid and not device_uuid:
            raise HTTPException(status_code=400, detail="Either uuid or device_uuid is required")
        if uuid and device_uuid:
            raise HTTPException(status_code=400, detail="Choose either uuid or device_uuid, not both")

        if uuid:
            mini_program = get_mini_program_by_uuid(db, uuid, state)
            if not mini_program:
                raise HTTPException(status_code=400, detail="No data was queried")
        else:
            mini_program = get_mini_program_by_device_uuid(db, device_uuid, state)
            if not mini_program:
                raise HTTPException(status_code=400, detail="No data was queried")
            uuid = mini_program.uuid

        mini_program_names = get_mini_program_name_by_uuid(db, uuid)
        mini_program_package = get_mini_program_package_by_uuid(db, uuid)
        mini_program['names'] = mini_program_names
        mini_program['package'] = mini_program_package

        return mini_program
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


@app.get("/programs")
async def get_programs(token: str = Depends(oauth2_scheme),
                             state: str = Query(..., description="A required parameter"),
                             db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Successful verification
        if not state:
            raise HTTPException(status_code=400, detail="State is required")
        programs = []
        mini_programs = get_mini_program_by_state(db, state)
        if mini_programs:
            for mini_program in mini_programs:
                uuid = mini_program.get('uuid')
                mini_program['names'] = get_mini_program_name_by_uuid(db, uuid)
                mini_program['packages'] = get_mini_program_package_by_uuid(db, uuid)
                programs.append(mini_program)
        return programs
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


@app.get("/program/uuid/")
async def get_programs(token: str = Depends(oauth2_scheme),
                             device_uuid: str = Query(..., description="A required parameter"),
                             db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Successful verification
        if not device_uuid:
            raise HTTPException(status_code=400, detail="device_uuid is required")
        uuid = get_mini_program_uuid_by_device_uuid(db, device_uuid)
        return {'uuid': uuid}
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


@app.post("/device")
async def add_device(token: str = Depends(oauth2_scheme),
                             uuid: str = Query(..., description="A required parameter"),
                             mini_program_uuid: str = Query(..., description="A required parameter"),
                             db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Successful verification
        if not uuid or not mini_program_uuid:
            raise HTTPException(status_code=400, detail="device_uuid or mini_program_uuid is required")
        res = insert_one_device(db, uuid, mini_program_uuid)
        if res == True:
            return {'Code': 200, 'detail': 'Inserted successfully'}
        else:
            raise HTTPException(status_code=400, detail="Insertion failure")
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


@app.delete("/device/{id}")
async def delete_device(token: str = Depends(oauth2_scheme),
                             id: int = Path(..., description="A required parameter"),
                             db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Successful verification
        if not id:
            raise HTTPException(status_code=400, detail="device_id is required")
        res = delete_device_by_id(db, id)
        if res == True:
            return {'detail': 'Inserted successfully'}
        elif res:
            raise HTTPException(status_code=400, detail="ID does not exist")
        else:
            raise HTTPException(status_code=400, detail="Delete failure")
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


@app.get("/devices")
async def get_devices(token: str = Depends(oauth2_scheme),
                             current: int = Query(..., description="A required parameter"),
                             pageSize: int = Query(..., description="A required parameter"),
                             db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Successful verification
        if not current or not pageSize:
            raise HTTPException(status_code=400, detail="pageSize or current is required")

        devices = query_device_by_limit(db, current, pageSize)
        return devices

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


@app.post("/program")
async def insert_program(item: ProgramItem,
                         token: str = Depends(oauth2_scheme),
                         db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Successful verification

        uuid = item.uuid
        icon = item.icon
        device_uuid = item.device_uuid
        names = item.names

        if not uuid or not icon or not device_uuid or not names:
            raise HTTPException(status_code=400, detail="Missing parameter")

        res_program = insert_one_mini_program(db, uuid, icon, device_uuid)
        res_program_name = insert_one_program_name(db, uuid, names)
        if res_program and res_program_name:
            return {'Code': 200, 'detail': 'Inserted successfully'}
        else:
            delete_program_by_uuid(db, uuid)
            delete_program_name_by_uuid(db, uuid)
            raise HTTPException(status_code=400, detail="Insertion failure")

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


@app.delete("/program/{uuid}")
async def delete_program(token: str = Depends(oauth2_scheme),
                             uuid: int = Path(..., description="A required parameter"),
                             db: Session = Depends(get_db)):
    try:
        # Verify the token
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Successful verification
        if not uuid:
            raise HTTPException(status_code=400, detail="uuid is required")
        res = delete_program_by_uuid(db, uuid)
        if res == True:
            return {'detail': 'Delete successfully'}
        else:
            raise HTTPException(status_code=400, detail="Delete failure")
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1012)
