from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import hashlib
import magic
import pandas as pd
import json
from datetime import datetime
from typing import List, Optional
import PyPDF2
from pydantic import BaseModel

from models.taxonomy import AssetData, FinancialData, ContractData, RegulatoryMapping
from utils.auth import get_current_user

upload = APIRouter(prefix="/upload", tags=["upload"])

# Configure upload directories
UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")
ALLOWED_EXTENSIONS = {
    "csv": ["text/csv", "application/csv"],
    "xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
    "pdf": ["application/pdf"],
    "json": ["application/json"],
    "txt": ["text/plain"]
}

# Create upload directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "csv"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "pdf"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "excel"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "json"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "txt"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "processed"), exist_ok=True)

class UploadResponse(BaseModel):
    file_id: str
    original_filename: str
    upload_path: str
    file_type: str
    size_bytes: int
    upload_time: datetime
    content_summary: Optional[dict] = None
    status: str = "success"


class UploadManager:
    """Manages file uploads, validation, and processing."""
    
    @staticmethod
    def validate_file_type(file: UploadFile) -> str:
        """Validate file type using magic numbers and extension."""
        # Read the first 2048 bytes for mime type detection
        file.file.seek(0)
        header = file.file.read(2048)
        file.file.seek(0)  # Reset file pointer
        
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(header)
        
        # Get extension from filename
        ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ""
        
        # Check if extension is allowed and mime type matches
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File extension '{ext}' not allowed")
        
        if detected_mime not in ALLOWED_EXTENSIONS[ext]:
            raise HTTPException(
                status_code=400, 
                detail=f"File content doesn't match extension. Detected: {detected_mime}"
            )
            
        return ext
    
    @staticmethod
    def generate_file_id(file: UploadFile) -> str:
        """Generate a unique file ID based on filename, content hash, and timestamp."""
        file.file.seek(0)
        content = file.file.read(8192)  # Read first 8K for hashing
        file.file.seek(0)  # Reset file pointer
        
        # Create unique ID
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.sha256(content).hexdigest()[:8]
        unique_id = f"{uuid.uuid4().hex[:8]}-{content_hash}"
        
        return unique_id
    
    @staticmethod
    def save_file(file: UploadFile, file_type: str, file_id: str) -> str:
        """Save uploaded file to appropriate directory with unique ID."""
        # Determine subdirectory based on file type
        if file_type == "xlsx":
            subdir = "excel"
        else:
            subdir = file_type
            
        # Create safe filename
        safe_filename = f"{file_id}_{file.filename}"
        upload_path = os.path.join(UPLOAD_DIR, subdir, safe_filename)
        
        # Save file
        with open(upload_path, "wb") as buffer:
            file.file.seek(0)
            shutil.copyfileobj(file.file, buffer)
            
        return upload_path
    
    @staticmethod
    def generate_content_summary(file_path: str, file_type: str) -> dict:
        """Generate a summary of the file contents based on file type."""
        summary = {}
        
        try:
            if file_type == "csv":
                df = pd.read_csv(file_path)
                summary = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": df.columns.tolist(),
                    "preview": df.head(5).to_dict() if not df.empty else {}
                }
                
            elif file_type == "xlsx":
                df = pd.read_excel(file_path)
                summary = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": df.columns.tolist(),
                    "preview": df.head(5).to_dict() if not df.empty else {}
                }
                
            elif file_type == "pdf":
                with open(file_path, "rb") as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    page_count = len(pdf_reader.pages)
                    text_preview = pdf_reader.pages[0].extract_text()[:500] if page_count > 0 else ""
                    summary = {
                        "page_count": page_count,
                        "text_preview": text_preview
                    }
                    
            elif file_type == "json":
                with open(file_path, "r") as json_file:
                    json_data = json.load(json_file)
                    if isinstance(json_data, dict):
                        keys = list(json_data.keys())
                        summary = {
                            "keys": keys[:10],  # First 10 keys
                            "structure": str(type(json_data)),
                            "key_count": len(keys)
                        }
                    elif isinstance(json_data, list):
                        summary = {
                            "item_count": len(json_data),
                            "structure": str(type(json_data)),
                            "sample": json_data[0] if json_data else None
                        }
                        
            elif file_type == "txt":
                with open(file_path, "r") as txt_file:
                    text = txt_file.read(1000)  # First 1000 chars
                    lines = text.count('\n') + 1
                    summary = {
                        "preview": text,
                        "line_count_preview": lines,
                        "character_count_preview": len(text)
                    }
                    
        except Exception as e:
            summary = {"error": f"Failed to generate summary: {str(e)}"}
            
        return summary


@upload.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a file with optional metadata.
    
    Supports CSV, XLSX, PDF, JSON, and TXT files.
    """
    # Validate file
    file_type = UploadManager.validate_file_type(file)
    
    # Generate unique ID
    file_id = UploadManager.generate_file_id(file)
    
    # Save file
    upload_path = UploadManager.save_file(file, file_type, file_id)
    
    # Get file size
    file_size = os.path.getsize(upload_path)
    
    # Generate content summary
    content_summary = UploadManager.generate_content_summary(upload_path, file_type)
    
    # Create response
    response = UploadResponse(
        file_id=file_id,
        original_filename=file.filename,
        upload_path=upload_path,
        file_type=file_type,
        size_bytes=file_size,
        upload_time=datetime.now(),
        content_summary=content_summary
    )
    
    # Track upload in database (mock implementation)
    # In a real system, you would store this in a database
    upload_record = {
        **response.dict(),
        "user_id": current_user.get("id", "anonymous"),
        "description": description,
        "category": category
    }
    
    # For demo purposes, save to a JSON file
    upload_records_file = os.path.join(UPLOAD_DIR, "upload_records.json")
    try:
        if os.path.exists(upload_records_file):
            with open(upload_records_file, "r") as f:
                records = json.load(f)
        else:
            records = []
            
        records.append({
            **upload_record,
            "upload_time": upload_record["upload_time"].isoformat()  # Convert datetime to string
        })
        
        with open(upload_records_file, "w") as f:
            json.dump(records, f, indent=2)
    except Exception as e:
        print(f"Failed to save upload record: {str(e)}")
    
    return response


@upload.post("/bulk", response_model=List[UploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    category: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload multiple files at once."""
    responses = []
    
    for file in files:
        try:
            # Validate file
            file_type = UploadManager.validate_file_type(file)
            
            # Generate unique ID
            file_id = UploadManager.generate_file_id(file)
            
            # Save file
            upload_path = UploadManager.save_file(file, file_type, file_id)
            
            # Get file size
            file_size = os.path.getsize(upload_path)
            
            # Generate content summary
            content_summary = UploadManager.generate_content_summary(upload_path, file_type)
            
            # Create response
            response = UploadResponse(
                file_id=file_id,
                original_filename=file.filename,
                upload_path=upload_path,
                file_type=file_type,
                size_bytes=file_size,
                upload_time=datetime.now(),
                content_summary=content_summary
            )
            
            responses.append(response)
            
        except Exception as e:
            # Log error but continue with other files
            print(f"Error uploading {file.filename}: {str(e)}")
            responses.append(UploadResponse(
                file_id=f"error-{uuid.uuid4().hex[:8]}",
                original_filename=file.filename,
                upload_path="",
                file_type="",
                size_bytes=0,
                upload_time=datetime.now(),
                status="error",
                content_summary={"error": str(e)}
            ))
    
    return responses


@upload.post("/assets-csv", response_model=dict)
async def upload_assets_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process a CSV file of asset data.
    Maps CSV columns to AssetData model.
    """
    # Validate file is CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Save file temporarily
    temp_path = os.path.join(UPLOAD_DIR, "csv", f"temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        file.file.seek(0)
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Read CSV
        df = pd.read_csv(temp_path)
        
        # Process data and convert to AssetData objects
        assets = []
        processed_count = 0
        error_count = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                asset_dict = row.to_dict()
                # Remove NaN values and convert to None
                asset_dict = {k: (None if pd.isna(v) else v) for k, v in asset_dict.items()}
                
                # Create AssetData object
                asset = AssetData(**asset_dict)
                assets.append(asset.dict())
                processed_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append({"row": row.to_dict(), "error": str(e)})
        
        # Save processed data
        output_path = os.path.join(UPLOAD_DIR, "processed", f"assets_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(output_path, "w") as f:
            json.dump(assets, f, indent=2)
        
        return {
            "status": "success",
            "processed_count": processed_count,
            "error_count": error_count,
            "errors": errors[:10],  # Return first 10 errors
            "output_path": output_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@upload.post("/financials-csv", response_model=dict)
async def upload_financials_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process a CSV file of financial data.
    Maps CSV columns to FinancialData model.
    """
    # Validate file is CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Save file temporarily
    temp_path = os.path.join(UPLOAD_DIR, "csv", f"temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        file.file.seek(0)
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Read CSV
        df = pd.read_csv(temp_path)
        
        # Process data and convert to FinancialData objects
        financials = []
        processed_count = 0
        error_count = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                financial_dict = row.to_dict()
                # Remove NaN values and convert to None
                financial_dict = {k: (None if pd.isna(v) else v) for k, v in financial_dict.items()}
                
                # Create FinancialData object
                financial = FinancialData(**financial_dict)
                financials.append(financial.dict())
                processed_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append({"row": row.to_dict(), "error": str(e)})
        
        # Save processed data
        output_path = os.path.join(UPLOAD_DIR, "processed", f"financials_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(output_path, "w") as f:
            json.dump(financials, f, indent=2)
        
        return {
            "status": "success",
            "processed_count": processed_count,
            "error_count": error_count,
            "errors": errors[:10],  # Return first 10 errors
            "output_path": output_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@upload.post("/contracts-csv", response_model=dict)
async def upload_contracts_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process a CSV file of contract data.
    Maps CSV columns to ContractData model.
    """
    # Validate file is CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Save file temporarily
    temp_path = os.path.join(UPLOAD_DIR, "csv", f"temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        file.file.seek(0)
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Read CSV
        df = pd.read_csv(temp_path)
        
        # Process data and convert to ContractData objects
        contracts = []
        processed_count = 0
        error_count = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                contract_dict = row.to_dict()
                # Remove NaN values and convert to None
                contract_dict = {k: (None if pd.isna(v) else v) for k, v in contract_dict.items()}
                
                # Create ContractData object
                contract = ContractData(**contract_dict)
                contracts.append(contract.dict())
                processed_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append({"row": row.to_dict(), "error": str(e)})
        
        # Save processed data
        output_path = os.path.join(UPLOAD_DIR, "processed", f"contracts_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(output_path, "w") as f:
            json.dump(contracts, f, indent=2)
        
        return {
            "status": "success",
            "processed_count": processed_count,
            "error_count": error_count,
            "errors": errors[:10],  # Return first 10 errors
            "output_path": output_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@upload.get("/files", response_model=List[dict])
async def list_uploaded_files(
    file_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all uploaded files with optional filtering by file type."""
    upload_records_file = os.path.join(UPLOAD_DIR, "upload_records.json")
    
    if not os.path.exists(upload_records_file):
        return []
    
    try:
        with open(upload_records_file, "r") as f:
            records = json.load(f)
            
        # Filter by file type if provided
        if file_type:
            records = [r for r in records if r.get("file_type") == file_type]
            
        # Sort by upload time (newest first)
        records.sort(key=lambda x: x.get("upload_time", ""), reverse=True)
        
        return records
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@upload.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an uploaded file by ID."""
    upload_records_file = os.path.join(UPLOAD_DIR, "upload_records.json")
    
    if not os.path.exists(upload_records_file):
        raise HTTPException(status_code=404, detail="No upload records found")
    
    try:
        # Read records
        with open(upload_records_file, "r") as f:
            records = json.load(f)
            
        # Find the file record
        file_record = None
        updated_records = []
        
        for record in records:
            if record.get("file_id") == file_id:
                file_record = record
            else:
                updated_records.append(record)
                
        if not file_record:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
            
        # Delete the actual file
        file_path = file_record.get("upload_path")
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Update records
        with open(upload_records_file, "w") as f:
            json.dump(updated_records, f, indent=2)
            
        return {"status": "success", "message": f"File {file_id} deleted"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")