from typing import List, Dict
from os import getenv
import json
import cx_Oracle
import cx_Oracle_async
import aiofiles


async def get_data() -> List[Dict[str, str]]:
    try:
        oracle_pool = await cx_Oracle_async.create_pool(
            user=getenv('ORACLE_USER'),
            password=getenv('ORACLE_PASSWORD'),
            dsn=getenv('ORACLE_DSN'),
        )

        async with oracle_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                async with aiofiles.open('bot/app/api.sql', mode='r') as file:
                    sql = await file.read()

                await cursor.execute(sql)
                rows = await cursor.fetchall()

        await oracle_pool.close()

        results = []
        for row in rows:
            row_dict = {
                "CRM": row[0],
                "CITY": row[5],
                "WORKSITE_SHORT_NAME": row[7],
                "ASSIGNEE_NAME": row[8],
                "OPEN_DATE": row[10],
                "CREATE_KI": row[11],
                "START_KI": row[12],
                "STOP_KI": row[13],
                "CLOSE_KI": row[14],
                "KS_3": row[15],
                "KS_23": row[16],
                "COMMENTARY": row[23],
                "LOGIN": row[24],
                "DATE_CLOSE": row[25],
            }

            results.append(row_dict)

        json_string = json.dumps(results, default=str, ensure_ascii=False)

        rows = json.loads(json_string)
        crm_by_dict = {row['CRM']: row for row in rows}
        items = list(crm_by_dict.values())

        return items

    except cx_Oracle.DatabaseError as e:
        print(e)
        return []
