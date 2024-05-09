from motor.motor_asyncio import AsyncIOMotorClient


class FilesDatabase:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db["files"]

    async def create_file(self, file_id, file_name, duration, caption, stream_link, message_id, chat_id, thumbnail=None):
        default_thumbnail = "https://i.pinimg.com/736x/0c/32/97/0c3297f3516a415219c7e89e16a4a3d2.jpg"
        return await self.col.insert_one(
            {
                "file_id": file_id,
                "file_name": file_name,
                "duration": duration,
                "caption": caption,
                "stream_link": stream_link,
                "message_id": message_id,
                "chat_id": chat_id,
                "thumbnail": thumbnail or default_thumbnail,
            }
        )

    async def get_file(self, file_id):
        return await self.col.find_one({"_id": file_id})

    async def get_all_files(self):
        return await self.col.find({}).to_list(length=None)

    async def update_file(self, file_id, data, tag="set"):
        await self.col.update_one({"_id": file_id}, {f"${tag}": data})

    async def delete_file(self, file_id):
        await self.col.delete_one({"_id": file_id}) 

    async def delete_file_by_message_id(self, message_id, chat_id):
        await self.col.delete_one({"message_id": message_id, "chat_id": chat_id})