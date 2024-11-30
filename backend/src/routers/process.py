from fastapi import APIRouter, Depends, UploadFile
from uuid import uuid4
from db import get_database, Session
from s3 import s3_connection

import errors

router = APIRouter()
