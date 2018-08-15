from tempfile import TemporaryFile

from io import BytesIO
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible
from .models import FileUpload
from .backblaze_b2 import BackBlazeB2
from django.core.cache import cache

@deconstructible
class B2Storage(Storage):
    def __init__(self, account_id=None, app_key=None, bucket_name=None):
        overrides = locals()
        defaults = {
            'account_id': settings.BACKBLAZEB2_ACCOUNT_ID,
            'app_key': settings.BACKBLAZEB2_APP_KEY,
            'bucket_name': settings.BACKBLAZEB2_BUCKET_NAME,
        }
        kwargs = {k: overrides[k] or v for k, v in defaults.items()}
        self.b2 = BackBlazeB2(**kwargs)

    def save(self, name, content, max_length=None):
        """
        Save and retrieve the filename.
        If the file exists it will make another version of that file.
        """

        resp = self.b2.upload_file(name, content)
        if 'fileName' in resp:
            #if self.b2.bucket_name != settings.BACKBLAZEB2_BUCKET_NAME:
            #   return self.url(name)
            file_upload = FileUpload()
            file_upload.file_id = resp['fileId']
            file_upload.name = resp['fileName']
            file_upload.content_sha1 = resp['contentSha1']
            file_upload.size = resp['contentLength']
            file_upload.save()

            return resp['fileName']

        else:
            # Raise exception
            print("Entramos en else no se porque")
            pass

    def exists(self, name):
        '''
        BackBlaze B2 does not have a method to retrieve a filename info.
        To get the info you need to make a download request, it will request the whole body.
        imagine a file of 1 GB to only get the file info.
        you can also list all files in that directory in chunks of 1000 imagine a directory of 10000.
        For now it will only request return False.
        '''

        return False

    def _temporary_storage(self, contents):
        '''
        Use this to return file objects
        '''

        conent_file = TemporaryFile(contents, 'r+')
        return conent_file

    def open(self, name, mode='rb'):
        resp = self.b2.download_file(name)

        output = BytesIO()
        output.write(resp)
        output.seek(0)
        return File(output, name)

    def url(self, name):
        return self.b2.get_file_url(name)

    #def get_available_name(self, name, max_length=None):
    #    return self.b2.download_url + '/'+ self.b2.bucket_name + '/'+ name

    def delete(self, name):
        try:
            file_upload = FileUpload.objects.get(name=name)
            res = self.b2.b2_delete_file_version(file_upload.file_id,file_upload.name)
            print(res)
            if 'fileName' in res:

                file_upload.delete()
                print("Hemos borrado el archivo")

        except FileUpload.DoesNotExist:
            print("No puedo borrar el archivo")
            pass

        pass

    def exists(self, name):
        try:
            FileUpload.objects.get(name=name)
            return True
        except FileUpload.DoesNotExist:
            return False

    def size(self, name):
        try:
            file_upload = FileUpload.objects.get(name=name)
            return file_upload['size']

        except FileUpload.DoesNotExist:
            return 0
            pass

