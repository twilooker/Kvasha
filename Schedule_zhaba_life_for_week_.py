from telethon import TelegramClient
import asyncio
from datetime import timedelta
import time

# Remember to use your own values from my.telegram.org!
api_id = 12345678  # your id
api_hash = 'your_hash'  # your hash

client = TelegramClient('anon', api_id, api_hash)
chat_id = -1234567890123  # your chat id where bot is added
loop = asyncio.get_event_loop()

text = None


# to get current status information
async def get_info():
    a = await client.send_message(chat_id, 'Жаба инфо')
    time.sleep(0.5)
    frog_info = await client.get_messages(chat_id, ids=a.id + 1)
    return frog_info.message


# to parse needed values
async def parse_message(text):
    text_spl = text.splitlines()
    time_work = text_spl[0].split(" ")[-1]
    time_eat = text_spl[1].split(" ")[-1]
    time_till_work_h = int(time_work.split(":")[0][:-1])
    time_till_work_m = int(time_work.split(":")[1][:-1])

    time_till_eat_h = int(time_eat.split(":")[0][:-1])
    time_till_eat_m = int(time_eat.split(":")[1][:-1])

    return time_till_work_h, time_till_work_m, time_till_eat_h, time_till_eat_m


# to delete scheduled messages if present
async def delete_scheduled():
    async for message in client.iter_messages(chat_id, scheduled=True):
        await client.delete_messages(chat_id, message.id)


# to schedule different kinds of activities
async def schedule_feeding(time_till_eat_h, time_till_eat_m):
    for t in range(28):  # 4 per day for 7 days
        await client.send_message(chat_id, 'Покормить жабу',
                                  schedule=timedelta(hours=t * 6 + time_till_eat_h, minutes=t + time_till_eat_m))


async def schedule_working(time_till_work_h, time_till_work_m):
    for t in range(21):  # 3 per day for 7 days
        await client.send_message(chat_id, 'Поход в столовую',
                                  schedule=timedelta(hours=t * 8 + time_till_work_h, minutes=t + time_till_work_m))
        await client.send_message(chat_id, 'Завершить работу', schedule=timedelta(hours=t * 8 + time_till_work_h + 2,
                                                                                  minutes=t + time_till_work_m + 1))


async def main():
    await client.start()

    global text
    text = await get_info()
    text_spl = text.splitlines()
    time_work = text_spl[0].split(" ")[-1]
    time_eat = text_spl[1].split(" ")[-1]

    await delete_scheduled()

    if ":" not in (time_work or time_eat):
        print("\nEnter loop: if : not in time_work or time_eat")

        if "Жабу можно покормить" in text:
            print("found: Жабу можно покормить")
            await client.send_message(chat_id, 'Покормить жабу')
            await schedule_feeding(6, 0)
        elif "Можно покормить через" in text:
            print("found: Можно покормить через")
            time_till_eat_h = int(time_eat.split(":")[0][:-1])
            time_till_eat_m = int(time_eat.split(":")[1][:-1])

            await client.send_message(chat_id, 'Завершить работу',
                                      schedule=timedelta(hours=time_till_eat_h, minutes=time_till_eat_m))
            await schedule_feeding(8 + time_till_eat_h, time_till_eat_m)

        if "Можно забрать жабу с работы" in text:
            print("found: Можно забрать жабу с работы")
            await client.send_message(chat_id, 'Завершить работу')
            # global text
            text = await get_info()
            time_till_work_h, time_till_work_m, time_till_eat_h, time_till_eat_m = \
                await parse_message(text)
            await schedule_working(time_till_work_h, time_till_work_m)
        elif "Жабу можно отправить на работу" in text:
            print("found: Жабу можно отправить на работу")
            await client.send_message(chat_id, 'Поход в столовую')
            await schedule_working(8, 0)
        elif "Забрать жабу можно через" in text:
            print("found: Забрать жабу можно через")
            work_line = text_spl[0].split(" ")
            time_till_work_h = int(work_line[4])
            time_till_work_m = int(work_line[6])
            await client.send_message(chat_id, 'Завершить работу',
                                      schedule=timedelta(hours=time_till_work_h, minutes=time_till_work_m))
            await schedule_working(8 + time_till_work_h, time_till_work_m)
    else:
        # global text
        text = await get_info()
        time_till_work_h, time_till_work_m, time_till_eat_h, time_till_eat_m = await parse_message(text)
        await schedule_feeding(time_till_eat_h, time_till_eat_m)
        await schedule_working(time_till_work_h, time_till_work_m)

    # await client.run_until_disconnected()
    # await client.disconnect()


loop.run_until_complete(main())

# %%
