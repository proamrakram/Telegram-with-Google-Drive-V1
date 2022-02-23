import datetime
import os
import enum
import gspread
from telethon import TelegramClient, events
from peewee import *


# Google Sheet Lib
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials
from moviepy.editor import VideoFileClip

# Google Drive Uploading Lib
from googleapiclient.http import MediaFileUpload
from Google import Create_Service

# Google Sheet Config
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


creds = ServiceAccountCredentials.from_json_keyfile_name("authSheet.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Telegram Videos").sheet1  # Open the spreadhseet

# Google Drive Config
CLIENT_SECRET_FILE = "authGoogleDrive.json"
API_NAME = "drive"
API_VERSION = "V3"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

# TelegramBot
api_id = 2905516
api_hash = "1627385b92cfed0d4cbc9358389289db"
client = TelegramClient("session", api_id, api_hash)
Group_Id = -1001555209007

services = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


class Database:
    def __init__(self, name) -> None:
        self.name = name

    def createDB(self):

        db = SqliteDatabase(self.name)
        db.connect()
        return db

    def CheckDB(self):
        result = os.path.exists(self.name)
        if result:
            return result
        else:
            print(result)
            result = self.createDB()
            return result


db = Database("data.db").createDB()


class Vedio(Model):
    id = AutoField().primary_key
    name = CharField(default=None)
    vedio_type = CharField()
    size = IntegerField()
    duration = IntegerField()
    year_mouth_day = DateField(default=datetime.datetime.now())
    hour_minute_second = TimeField(default=datetime.datetime.now())
    all_times = DateTimeField(default=datetime.datetime.now())
    timestapms = TimestampField(default=datetime.datetime.now())
    year = IntegerField(default=datetime.datetime.now().year)
    month = IntegerField(default=datetime.datetime.now().month)
    folder_id = TextField()
    main_folder_id = TextField()
    url = TextField()

    class Meta:
        database = db  # this model uses the "people.db" database


class sizeUnit(enum.Enum):
    # class to store the various units
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4


def unitConvertor(sizeInBytes, unit):
    # Cinverts the file unit
    if unit == sizeUnit.KB:
        return str(format(sizeInBytes / 1024, ".2f")) + " KB"
    elif unit == sizeUnit.MB:
        return str(format(sizeInBytes / (1024 * 1024), ".2f")) + " MB"
    elif unit == sizeUnit.GB:
        return str(format(sizeInBytes / (1024 * 1024 * 1024), ".2f")) + " GB"
    else:
        return sizeInBytes


def fileSize(filePath, size_type):
    """File size in KB, MB and GB"""
    size = os.path.getsize(filePath)
    return unitConvertor(size, size_type)


if db.table_exists(Vedio):
    pass
else:
    db.create_tables([Vedio])

client.start()


@client.on(
    events.NewMessage(
        chats=Group_Id,
    )
)
async def my_event_handler(event):

    # message = await client.get_messages(Group_Id, limit=1, )

    # message = await client.get_messages(Group_Id,filter=InputMessagesFilterVideo, limit=1,)
    message = event.message
    
    # DocumentAttributeFilename
    # DocumentAttributeVideo

    document = hasattr(message.media, "document")

    photo = hasattr(message.media, "photo")

    def modelExists(id):
        result = Vedio.get_or_none(id=id)
        return result

    def lastModel():
        result = modelExists(1)
        if result:
            lastModel = Vedio.select().order_by(Vedio.id.desc()).get()
            return lastModel
        else:
            return None

    def createMainFolder():
        last_Model = lastModel()
        if last_Model:
            main_folder_id = last_Model.main_folder_id
            return main_folder_id
        else:
            newFolder = "فيديوهات"

            folder_metadata = {
                "name": newFolder,
                "mimeType": "application/vnd.google-apps.folder",
            }

            file = services.files().create(body=folder_metadata).execute()

            Vedio.create(
                name="Null",
                vedio_type="Null",
                size="Null",
                duration="Null",
                folder_id=file.get("id"),
                main_folder_id=file.get("id"),
                url="Null",
            )
            return file.get("id")

    def createFolder(main_Folder_id):
        newFolder = (
            "فيديوهات شهر "
            + str(datetime.datetime.now().month)
            + "سنة "
            + str(datetime.datetime.now().year)
        )

        folder_metadata = {
            "name": newFolder,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [main_Folder_id],
        }

        file = services.files().create(body=folder_metadata).execute()

        Vedio.create(
            name="Null",
            vedio_type="Null",
            size="Null",
            duration="Null",
            folder_id=file.get("id"),
            main_folder_id=main_Folder_id,
            url="Null",
        )

        return file.get("id")

    def updateFolder():
        last_Model = lastModel()
        if last_Model:
            if (
                datetime.datetime.now().month == last_Model.month
                and datetime.datetime.now().year == last_Model.year
            ):

                return last_Model.folder_id

            else:
                folder_id = createFolder(last_Model.main_folder_id)

                return folder_id
        else:
            main_Folder_id = createMainFolder()
            folder_id = createFolder(main_Folder_id)
            return folder_id

    folder_id = updateFolder()

    main_Folder_id = createMainFolder()
    
    print(folder_id)

    def get_length(filename):

        clip = VideoFileClip(filename)

        duration = clip.duration

        clip.close()

        return duration

    def get_mime_type():

        mime_type = message.media.document.mime_type

        mime_types = {
            "video/mp4": ".mp4",
            "video/mpeg": ".mpeg",
            "video/webm": ".webm",
            "video/x-flv": ".flv",
            "application/x-mpegURL": ".m3u8",
            "video/MP2T": ".ts",
            "video/mp2t": ".ts",
            "video/3gpp": ".3gp",
            "video/quicktime": ".mov",
            "video/x-msvideo": ".avi",
            "video/x-ms-wmv": ".wmv",
            "video/ogg": ".ogv",
            "video/3gpp2": ".3g2",
            "video/x-theora+ogg": "ogg",
        }

        for key, value in mime_types.items():
            if mime_type == key:
                print("The mime_type is:" + str(mime_type))
                mimeType = {
                    "mimeType": mime_type,
                    "EXT": value,
                }
                return mimeType

        print("This mime type is not found")

        return False

    def time_video(duration, path):

        sample_str = "{}".format(message.media.document.attributes[0])

        DocumentAttributeFilename = sample_str[0:25]

        if DocumentAttributeFilename == "DocumentAttributeFilename":
            duration = get_length(path)

        video_time = str(datetime.timedelta(seconds=int(duration)))

        print(video_time)

        return video_time

    def get_video_data():

        array_video_info = {}

        sample_str = "{}".format(message.media.document.attributes[0])

        DocumentAttributeFilename = sample_str[0:25]

        if (0 <= 1) and (1 < len(message.media.document.attributes)):

            array_video_info["name"] = message.media.document.attributes[1].file_name
            array_video_info["mimeType"] = message.media.document.mime_type
            array_video_info["size"] = message.media.document.size

            if DocumentAttributeFilename == "DocumentAttributeFilename":
                array_video_info["time"] = "Null"
            else:
                array_video_info["time"] = message.media.document.attributes[0].duration

            array_video_info["True"] = True

            return array_video_info

        else:

            array_video_info["mimeType"] = message.media.document.mime_type
            array_video_info["size"] = message.media.document.size
            if DocumentAttributeFilename == "DocumentAttributeFilename":
                array_video_info["time"] = "Null"
            else:
                array_video_info["time"] = message.media.document.attributes[0].duration

            array_video_info["True"] = False
            return array_video_info

    def create_Video_Model(data):
        vedio = Vedio.create(
            name=data["name"],
            vedio_type=data["mimeType"],
            size=data["size"],
            duration=data["time"],
            folder_id=folder_id,
            main_folder_id=main_Folder_id,
            url="http://www.telegram.org",
        )

        print("Model video has been created!!")

        return vedio

    async def download_videos(path):

        await message.download_media(path)

        print("done downloaded")

        return True

    def set_size(path, vedio):

        file_size = fileSize(path, sizeUnit.MB)

        vedio.size = file_size

        vedio.save()

        print("File Size is :", file_size, "bytes")

    def uploadToGoogleDrive(file_name, path, folder_id, mime_type):

        file_metadata = {
            "name": file_name,
            "parents": [folder_id],
        }

        media = MediaFileUpload(path, mimetype=mime_type)

        file_id = (
            services.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        print("Video has been uploaded to your drive")

        return file_id

    def get_url_file(file_id, vedio):

        request_body = {"role": "reader", "type": "anyone"}

        response_permission = (
            services.permissions().create(fileId=file_id, body=request_body).execute()
        )

        response_share_link = (
            services.files().get(fileId=file_id, fields="webViewLink").execute()
        )

        vedio.url = response_share_link["webViewLink"]

        vedio.save()

        return response_share_link["webViewLink"]

    def insertDataToSheet(vedio):

        col = sheet.col_values(1)[-1]

        if col == "الترتيب التسلسلي":
            col = 1
        else:
            col = int(col) + 1

        insertRow = [
            str(col),
            str(vedio.name),
            str(vedio.vedio_type),
            str(vedio.size),
            str(vedio.duration),
            str(vedio.all_times),
            str(vedio.url),
        ]

        row = sheet.append_row(insertRow)

        print("These data has been added to sheet: ")

    def get_name_from_user(data):
        if message.message:

            data["name"] = message.message
        else:

            data["name"] = "vedio" + str(vedio.id)

        return data["name"]

    if document:

        mime_type = get_mime_type()

        if mime_type:

            data = get_video_data()

            if data["True"]:

                print("The Info of Video are: ")

                print(
                    str(data["size"])
                    + "\n"
                    + str(data["mimeType"])
                    + "\n"
                    + str(data["time"])
                    + "\n"
                    + str(data["name"])
                )

                vedio = create_Video_Model(data)

                path = "./videos/" + str(vedio.name)

                await download_videos(path)

                set_size(path, vedio)

                file_id = uploadToGoogleDrive(
                    str(vedio.name), path, folder_id, vedio.vedio_type
                )

                url = get_url_file(file_id["id"], vedio)

                time = time_video(vedio.duration, path)

                vedio.duration = time

                vedio.save()

                insertDataToSheet(vedio)

                os.remove(path)

                print("The Vedio has been deleted")

            else:
                data["name"] = "vedio"

                vedio = create_Video_Model(data)

                name = get_name_from_user(data)

                vedio.name = name

                vedio.save()

                print("The Info of Video are: ")

                print(
                    str(data["size"])
                    + "\n"
                    + str(data["mimeType"])
                    + "\n"
                    + str(data["time"])
                    + "\n"
                    + str(data["name"])
                )

                path = "./videos/" + str(vedio.name) + mime_type["EXT"]

                await download_videos(path)

                set_size(path, vedio)

                file_id = uploadToGoogleDrive(
                    str(vedio.name), path, folder_id, vedio.vedio_type
                )

                url = get_url_file(file_id["id"], vedio)

                time = time_video(vedio.duration, path)

                vedio.duration = time

                vedio.save()

                insertDataToSheet(vedio)

                os.remove(path)

                print("The Vedio has been deleted")

        else:
            print("Not Vedio")

    else:
        print("not Video")


client.run_until_disconnected()
