import uuid
import os

from flask import jsonify, request, Blueprint

from service import FileDao, ClientFilesDao, ClientDao
from storage import AzureStorage
from utils import FileUtil, ShortUrlUtil

files_bp = Blueprint('files', __name__)

@files_bp.route("/files/upload", methods=["POST"])
def files_upload():
    try:
        client_id = request.args.get("clientId")

        if client_id is None:
            return jsonify(
                message = "ClientId is not provided"
            )

        if 'file' not in request.files:
            return jsonify(
                message = "No file part"
            ), 400

        client_parameters = ClientDao.find_client_plan_parameters(client_id)

        extensions = client_parameters['extensions']

        file = request.files['file']
        extension = FileUtil.extract_file_extension(file.filename)

        if extension not in extensions:
            return jsonify(
                message = "File extension not allowed"
            ), 400

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        max_size = client_parameters['maxSize']

        if file_size >= max_size:
            return jsonify(
                message = f"File too large, max value accepted is {max_size / 1024 / 1024}mb"
            )

        client_files_count = ClientFilesDao.get_count_client_files(client_id)
        max_upload = client_parameters['maxFilesUpload']

        if client_files_count >= max_upload:
            return jsonify(
                message = "Client has reached max amount of uploads"
            )

        file_id = str(uuid.uuid4())
        blob_name = f"{file_id}.{extension}"
        filename = file.filename[:255]

        long_url = AzureStorage.upload_file_to_azure(blob_name, file)
        url = ShortUrlUtil.shorten_url(long_url)

        FileDao.insert_file(file_id, filename, file_size, extension, url)
        ClientFilesDao.insert_file_for_client(client_id, file_id)

        return jsonify(
            fileId = file_id,
            fileUrl = f"{url}"
        )
    except Exception as ex:
        return jsonify(
            error = ex.args
        ), 500


@files_bp.route("/files/delete", methods=["DELETE"])
def files_delete():
    try:
        client_id = request.json['clientId']
        file_url = request.json['fileUrl']

        success_delete_azure = AzureStorage.delete_file_from_azure(file_url)

        if success_delete_azure:
            ClientFilesDao.delete_file_from_client(client_id, file_url)
            FileDao.delete_file(file_url)
        else :
            return jsonify(
                message = "Something went wrong while deleting file on Azure"
            ), 500

        return jsonify(
            message = "File deleted"
        )
    except Exception as ex:
        return jsonify(
            message = "Something went wrong",
            error = ex.args
        ), 500