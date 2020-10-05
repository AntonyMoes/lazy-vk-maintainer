import aiohttp
import asyncio
import aiovk
import json
from dataclasses import dataclass
from typing import List, Optional
from utils import get_env_var


TOKEN = get_env_var('TOKEN')
GROUP_ID = get_env_var('GROUP_ID', t=int)
APP_ID = get_env_var('APP_ID', t=int)
LOGIN = get_env_var('LOGIN')
PASSWORD = get_env_var('PASSWORD')


@dataclass
class PhotoAttachment:
    id: int
    owner_id: int


async def upload_photo_to_wall(api: aiovk.API, group_id: int,
                               file: str, caption: Optional[str] = None) -> PhotoAttachment:
    resp = await api.photos.getWallUploadServer(group_id=group_id)
    url = resp['upload_url']

    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('photo', open(file, 'rb'))
        async with session.post(url, data=data) as resp:
            resp = json.loads(await resp.text())
            server = int(resp['server'])
            hash = resp['hash']
            photo = resp['photo']

            params = {
                'group_id': group_id,
                'server': server,
                'hash': hash,
                'photo': photo
            }

            if caption:
                params['caption'] = caption

            resp = await api.photos.saveWallPhoto(**params)
            photo_id = int(resp[0]['id'])
            owner_id = int(resp[0]['owner_id'])
            return PhotoAttachment(photo_id, owner_id)


async def post_to_wall(api: aiovk.API, group_id: int,
                       text: Optional[str] = None,
                       photos: Optional[List[PhotoAttachment]] = None,
                       source: Optional[str] = None,
                       from_group: bool = True, signed: bool = False):
    assert text or photos or source, "No content to post"

    params = {
        'owner_id': -abs(group_id),
        'from_group': int(from_group),
        'signed': int(signed)
    }

    if text:
        params['message'] = text
    if photos:
        assert len(photos) <= 10, "Only 10 attchments at most are allowed"

        def encode(ph):
            return f'photo{ph.owner_id}_{ph.id}'

        params['attachments'] = ','.join(map(encode, photos))
    if source:
        params['copyright'] = source

    print(await api.wall.post(**params))


async def main():
    async with aiovk.ImplicitSession(LOGIN, PASSWORD, APP_ID, ['photos', 'wall']) as vk_session:
        api = aiovk.API(vk_session)
        photo = await upload_photo_to_wall(api, GROUP_ID, 'example.png')
        await post_to_wall(api, GROUP_ID, photos=[photo], text='test')


asyncio.get_event_loop().run_until_complete(main())
