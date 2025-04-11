import os
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator

from hospital_client.constant import (
    GOV_POLICY_SUMMARY_MAP,
    GOVT_DOC_DIR_PATH,
    HOS_POLICY_SUMMARY_MAP,
    HOSP_DOC_DIR_PATH,
)
from hospital_client.summarizer import (
    get_document_references,
    get_matching_documents,
    lookup_query,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows all origins, but you can specify a list like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Define the Enum for document types
class DocumentType(str, Enum):
    government = "government"
    hospital = "hospital"


# Pydantic model for doc_type validation
class UploadDocumentRequest(BaseModel):
    doc_type: str

    @validator("doc_type")
    def validate_type(cls, v):
        if v not in DocumentType.__members__:
            raise ValueError(f"doc_type {v} is not allowed")
        return v


# Define the response model
class UploadDocumentResponse(BaseModel):
    message: str
    doc_type: str
    doc_path: str


# Dependency function to validate both file and doc_type
async def validate_upload(file: UploadFile = File(...), doc_type: str = Form(...)):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Validate doc_type using the model
    if doc_type not in DocumentType.__members__:
        raise ValueError(f"doc_type {doc_type} is not allowed")
    return {"file": file, "doc_type": doc_type}


@app.post("/upload-document", response_model=UploadDocumentResponse)
async def upload_document(data=Depends(validate_upload)):
    file = data["file"]
    doc_type = data["doc_type"]
    cwd = os.getcwd()
    folder_location: Path
    if doc_type == DocumentType.government:
        folder_location = Path(os.path.join(cwd, GOVT_DOC_DIR_PATH))
    else:
        folder_location = Path(os.path.join(cwd, HOSP_DOC_DIR_PATH))
    # Save file
    filename = Path(file.filename).name
    file_path = os.path.join(folder_location, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "message": f"Document '{filename}' uploaded successfully.",
        "doc_type": doc_type,
        "doc_path": file_path,
    }


# Define the Pydantic model for the input
class DocumentRequest(BaseModel):
    doc_name: str
    doc_type: DocumentType

    # Custom validator for doc_type
    @validator("doc_type")
    def validate_type(cls, v):
        if v not in DocumentType:
            raise ValueError(f"doc_type {v} is not allowed")
        return v


# Define the response model
class DocumentSummary(BaseModel):
    doc_name: str
    doc_type: str
    doc_summary: str


@app.get("/summary", response_model=DocumentSummary)
async def get_document_summary(
    doc_name: str = Query(..., description="The string to search for."),
    doc_type: DocumentType = Query(..., description="The action to perform."),
):
    """
    Return a summary of the specified document, with type validation.
    """

    if doc_type not in DocumentType.__members__:
        raise HTTPException(status_code=404, detail="Document type is invalid.")

    if doc_type == DocumentType.government and doc_name not in GOV_POLICY_SUMMARY_MAP:
        raise HTTPException(
            status_code=404, detail="Government policy document not found."
        )
    elif doc_type == DocumentType.hospital and doc_name not in HOS_POLICY_SUMMARY_MAP:
        raise HTTPException(
            status_code=404, detail="Hospital policy document not found."
        )

    cwd = os.getcwd()
    file_location: Path
    if doc_type == DocumentType.government:
        file_location = Path(
            os.path.join(cwd, GOVT_DOC_DIR_PATH, "summary", doc_name + "_summary.txt")
        )
    else:
        file_location = Path(
            os.path.join(cwd, HOSP_DOC_DIR_PATH, "summary", doc_name + "_summary.txt")
        )

    with open(file_location, "r") as file:
        summary_text = file.read()

    # Simulated summary response
    return {
        "doc_name": doc_name,
        "doc_type": doc_type,
        "doc_summary": summary_text,
    }


# Define the Enum for the action types
class ActionType(str, Enum):
    get_document_references = "get_document_references"
    get_matching_documents = "get_matching_documents"
    lookup_query = "lookup_query"


# Define the Response model for matching documents
class MatchResult(BaseModel):
    document_names: List[str]


# Define the Response model for document references
class ReferenceResult(BaseModel):
    document_name: str
    reference: str


# Search endpoint with action validation
@app.get("/search", response_model=Union[MatchResult, ReferenceResult])
async def search_document(
    query: str = Query(..., description="The string to search for."),
    action: ActionType = Query(..., description="The action to perform."),
    filename: Optional[str] = Query(
        None, description="Optional filename to filter search"
    ),
):
    """
    Search documents by query. Two actions:
    - get_document_references: returns where the query appears in a document
    - get_matching_documents: returns document names where query appears
    """
    if action == ActionType.get_matching_documents:
        return MatchResult(document_names=await get_matching_documents(query))
    elif action == ActionType.get_document_references:
        if filename != "" and query != "":
            reference = await get_document_references(query, filename=filename)
            return ReferenceResult(document_name=filename, reference=reference)
        raise HTTPException(
            status_code=404, detail="Filename and query required for referencing"
        )
    elif action == ActionType.lookup_query:
        if query != "":
            answer = await lookup_query(query)
            return ReferenceResult(document_name=filename, reference=answer)
        raise HTTPException(status_code=404, detail="query required for checking")


# Optional: root for sanity check
@app.get("/health")
def health():
    return {"message": "Policy Document API"}
