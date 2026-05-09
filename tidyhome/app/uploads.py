from fastapi import UploadFile


async def selected_photo_upload(*uploads: UploadFile | None) -> tuple[UploadFile | None, bytes]:
    for upload in uploads:
        if not upload or not upload.filename:
            continue
        data = await upload.read()
        if data:
            return upload, data
    return None, b""
