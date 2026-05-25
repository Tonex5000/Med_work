from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.config import Settings, get_settings
from app.core.exceptions import FileTooLargeException
from app.services.drug_service import DrugClassifierService
from app.utils.file_processor import dataframe_to_output_bytes, parse_uploaded_file
from app.utils.http_client import get_http_client

router = APIRouter(tags=["drug-classification"])


async def get_drug_classifier_service(
    client=Depends(get_http_client),
) -> DrugClassifierService:
    settings = get_settings()
    return DrugClassifierService(client=client, settings=settings)


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload a CSV/XLSX file and return enriched Excel with therapeutic classes",
)
async def upload_drug_file(
    file: UploadFile = File(...),
    #settings: Settings = Depends(get_settings),
    service: DrugClassifierService = Depends(get_drug_classifier_service),
):

    settings = service.settings
    raw_content = await file.read()

    if len(raw_content) > settings.max_file_size_mb * 1024 * 1024:
        raise FileTooLargeException(f"File exceeds {settings.max_file_size_mb}MB limit")

    dataframe, _ = parse_uploaded_file(file.filename or "uploaded_file", raw_content)

    drugs = dataframe["Drug"].fillna("").astype(str).tolist()
    classifications = await service.classify_drugs(drugs)

    dataframe["Therapeutic Class"] = classifications
    output_bytes = dataframe_to_output_bytes(dataframe)

    headers = {"Content-Disposition": 'attachment; filename="processed_drugs.xlsx"'}
    return StreamingResponse(
        content=iter([output_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
