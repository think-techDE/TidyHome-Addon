from fastapi import UploadFile

from models import Task
from storage import add_comment, add_photo
from uploads import selected_photo_upload


def save_initial_task_note(task: Task, note: str, author: str = "") -> bool:
    return bool(add_comment("task", task.id, note, author=author))


async def save_initial_task_photo(task: Task, author: str = "",
                                  photo: UploadFile | None = None,
                                  photo_camera: UploadFile | None = None,
                                  photo_file: UploadFile | None = None) -> bool:
    selected_photo, data = await selected_photo_upload(photo, photo_camera, photo_file)
    if not selected_photo:
        return False
    return bool(add_photo("task", task.id, "before", selected_photo.filename or "",
                          selected_photo.content_type or "", data, author=author))
