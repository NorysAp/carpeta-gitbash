import sqlite3
import re
from datetime import datetime
import pytz
from skpy import Skype

# result_integration = eval(GetVar('result_integration'))
#start = datetime.strptime(GetVar('exec_start'), "%Y-%m-%d %H:%M:%S") if GetVar('exec_start') else ''
#nd = datetime.strptime(GetVar('exec_end'), "%Y-%m-%d %H:%M:%S") if GetVar('exec_start') else ''
qas_ids = {'Raquel' :'live:.cid.559343e394b6b7f', 
            'Yanitza' : 'live:.cid.41ed7cf0d5ad490',
            'Massiel': 'stickmassy',
            'Alexandra': 'live:.cid.9dfe39f2721fedfe'}
clinic_name = "Mortenson Dental"
descript = "\nResumen de prioridades:"

try:
        db_path = 'C:/Arch_per_DR/ws mortenson/Insurance_verification.db'
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
except Exception as e:
        raise Exception(f'Exception opening database: {str(e)}')

def get_message_header(clinic_name, workflow_person_id, workflow_person_name,descript, content) -> str:
    def _manners():
        greeting_text = 'Hola '
        return greeting_text

    return f'''{clinic_name}\n
{_manners()} <at id="{workflow_person_id}">{workflow_person_name}</at> :)\n{descript}\n
<b>{content}</b>\n '''

def get_all_with_rows_and_carriers(conn: sqlite3.Connection, start_datetime: str, end_datetime: str) -> list:
    """
    Returns a list of rows and carrier name with unique dates
    """
    sql = f'''
    
   SELECT s.Sheetname, cl.Practice 
   || ' | ' || c.Carriername
   || ' | Row ' || cl.Cellnum 
   || ' | ' || cl.VerificationStatus actives_with_rows_and_carrier
    FROM sheet s
    LEFT JOIN carrierlog cl ON cl.Sheetnum = s.Sheetnum
    LEFT JOIN carrier c ON c.Carriernum = cl.Carriernum 
    WHERE cl.ExectStartTime BETWEEN '{start_datetime}' AND '{end_datetime}'
    ORDER BY s.Sheetname,cl.Practice, c.Carriername
    
    '''

    print(f'\n\nget_actives_with_rows_and_carrier SQL:\n{sql}\n')

    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows_and_carriers = cur.fetchall()
        result_list = []

        previous_date = None
        for row_and_carrier in rows_and_carriers:
            sheet_name, row_carrier = row_and_carrier

            if sheet_name != previous_date:
                result_list.append(sheet_name)
                previous_date = sheet_name

            result_list.append(row_carrier)

        return result_list

    except sqlite3.Error as e:
        print(f'Error while getting the actives with additional info: \n\n{e}')
        return []


start='2023-08-15 02:10:43'
end='2023-08-24 13:03:39'

row = get_all_with_rows_and_carriers(conn,start ,end)
rows_with_new_line = "\n\n".join(row)

# Generar el mensaje de reporte general
mensaje_reporte_general = ""

mensaje_reporte_general += rows_with_new_line

print(mensaje_reporte_general)

chat_id_ = '19:46ad23668eac46518ed963ed37617087@thread.skype'
workflow_person_id = '@'
workflow_person_name = "test"
#chat_id_ = '19:f1c1f06680e246ae8c4b7d9a2817f098@thread.skype'
#workflow_person_id = qas_ids['Massiel']
#workflow_person_name = "Massy"


if len(mensaje_reporte_general) != 0:
    try:
        sk = Skype('dentalrobot@outlook.com', '*Skype2021*')
        group_chat = sk.chats[chat_id_]
        group_chat.sendMsg(get_message_header(clinic_name,workflow_person_id,workflow_person_name,descript,mensaje_reporte_general), rich=True)
    except Exception as e:
            raise Exception(f'Exception connecting to skype: {str(e)}')

from collections import defaultdict

# Supongamos que tienes los resultados de la consulta en una lista llamada 'results'
results = [
    {"Sheetname": "Clarksville", "actives_with_rows_and_carrier": "MetLife | Row 21 | Active"},
    {"Sheetname": "audubon", "actives_with_rows_and_carrier": "MetLife | Row 22 | Active"},
    {"Sheetname": "Iroquois", "actives_with_rows_and_carrier": "delta ins | Row 22 | Active"},
    {"Sheetname": "Landen", "actives_with_rows_and_carrier": "delta ins | Row 22 | Active"},
    {"Sheetname": "Orem", "actives_with_rows_and_carrier": "MetLife | Row 22 | Active"},
    {"Sheetname": "Sout siux", "actives_with_rows_and_carrier": "Aetna | Row 1 | Active"},
    {"Sheetname": "Jeffersonville", "actives_with_rows_and_carrier": "Aetna | Row 3 | Active"},
    # ... otros resultados ...
]

# Crear un diccionario para agrupar y contar los detalles por carrier
carrier_groups = defaultdict(list)

# Iterar a través de los resultados y agrupar por carrier
for result in results:
    sheetname = result["Sheetname"]
    details = result["actives_with_rows_and_carrier"].split(" | ")
    carrier_name = details[0]

    carrier_groups[carrier_name].append(details)

# Mostrar los resultados agrupados y contados
for carrier_name, details_list in carrier_groups.items():
    num_entries = len(details_list)
    sheetname = details_list[0][0]
    formatted_details = ", ".join([f"[{detail[1]}]" for detail in details_list])

    formatted_result = f"- Location: {sheetname} - 11512"
    formatted_result += f"\n -- {carrier_name}: {num_entries} entries: {formatted_details}\n"

    print(formatted_result)
