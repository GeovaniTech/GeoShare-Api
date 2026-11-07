from flask import Blueprint, request, jsonify

from service import RoomDao

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/rooms", methods=["PUT"])
def create_room():
    try:
        files = request.json['files']
        client_id = request.json['clientId']

        room_id = RoomDao.create_room(client_id)
        RoomDao.add_files_to_room(room_id, files)

        return jsonify(
            roomId = room_id
        )
    except Exception as ex:
        return jsonify(
            message = "Something went wrong",
            error = ex.args
        ), 500


@rooms_bp.route("/rooms/<room_id>", methods=["GET"])
def get_room(room_id):
    try:
        if not room_id.isdigit() or len(room_id) != 6:
            return jsonify(
                message = "Room code must have 6 digits"
            ), 400

        room = RoomDao.find_room(room_id)

        if room is None:
            return jsonify(
                message = "Room not found"
            ), 404

        files = RoomDao.find_room_files(room_id)

        return jsonify(
            roomId = room['id'],
            createdAt = room['created_at'].isoformat(),
            files = [
                {
                    "id": file['id'],
                    "filename": file['filename'],
                    "extension": file['extension'],
                    "size": file['size'],
                    "url": file['storage_url'],
                    "createdAt": file['created_at'].isoformat()
                }
                for file in files
            ]
        ), 200
    except Exception as ex:
        return jsonify(
            message = "Something went wrong",
            error = ex.args
        ), 500
