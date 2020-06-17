import hashlib

from . import config


def 上传(串, 容器):
    h = hashlib.md5()
    h.update(串)
    md5 = h.hexdigest()

    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(config.STORAGE_CONNECTION_STRING)

    blob_client = blob_service_client.get_blob_client(container=容器, blob=md5)
    try:
        blob_client.get_blob_properties()
    except:
        blob_client.upload_blob(data=串)

    return md5


def 下载(blob, 容器):
    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(config.STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=容器, blob=blob)
    download_stream = blob_client.download_blob()
    return download_stream.readall()
