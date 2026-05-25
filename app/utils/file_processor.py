from io import BytesIO
from pathlib import Path

import pandas as pd

from app.core.exceptions import InvalidFileTypeException, MissingDrugColumnException

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}


def parse_uploaded_file(file_name: str, content: bytes) -> tuple[pd.DataFrame, str]:
    ext = Path(file_name).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise InvalidFileTypeException("Only .csv and .xlsx files are supported")

    stream = BytesIO(content)

    if ext == ".csv":
        dataframe = pd.read_csv(stream)
    else:
        dataframe = pd.read_excel(stream)

    if "Drug" not in dataframe.columns:
        raise MissingDrugColumnException('Missing required column "Drug"')

    return dataframe, ext


def dataframe_to_output_bytes(dataframe: pd.DataFrame) -> bytes:
    output_stream = BytesIO()
    with pd.ExcelWriter(output_stream, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="classified_drugs")

    output_stream.seek(0)
    return output_stream.read()
