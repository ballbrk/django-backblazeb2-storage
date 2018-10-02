
from celery.task import Task
from b2_storage.models import FileUpload
try:
    from celery.utils.log import get_task_logger
except ImportError:
    from celery.log import get_task_logger

logger = get_task_logger(name=__name__)


class RemoveElement(Task):

    def run(self, file_id, name, **kwargs):
        file_upload = FileUpload.objects.get(file_id=file_id,name=name)
        file_upload.delete()


