import logging
from striprtf.striprtf import rtf_to_text
import io
from db.db_access import DatabaseAccess
import pandas as pd
import os

def anonymize_rtf(rtf_in: str) -> str:
    out_form: str = ""
    try:
        text = rtf_to_text(str(rtf_in))
        text_in = io.StringIO(text)
        text_out = io.StringIO()
        for line in text_in:
            if ('Paciente' in line) or ('Solicitado por:' in line):
                continue
            else:
                text_out.write(line)
        text_out.seek(0)
        out_form = text_out.getvalue()
    except:
        logging.error('FAIL TO CONVERT RTF IN TO TEXT')
    return out_form

def get_forms(date_id: list, db_access: DatabaseAccess) -> pd.DataFrame:
    df_result = pd.DataFrame(columns = ['DateID', 'Form'])
    L = len(date_id)
    N = 1000 if 1000 < L else L
    for s in range(0, L, N):
        d = tuple(date_id[s: s + N])
        if len(date_id) > 1:
            sql_query = f"SELECT IDCita AS DateID, \
                                 InformeRTF AS Form \
                          FROM CITAS_INFORMES \
                          WHERE IDCita IN {d} AND Numero = 1"
        else:
            sql_query = f"SELECT IDCita AS DateID, \
                                 InformeRTF AS Form \
                          FROM CITAS_INFORMES \
                          WHERE IDCita = {d} AND Numero = 1"
        df_tmp = db_access.run_query(sql_query)
        if df_tmp.empty:
            logging.error('NO FORMS RETURNED FROM QUERY')
        else:
            df_result = pd.concat([df_result, df_tmp], ignore_index=True)

    df_result.drop_duplicates(inplace=True)
    df_result['Form']  = df_result['Form'].apply(lambda x: anonymize_rtf(x))
    return df_result

def extract_forms(df: pd.DataFrame, db_access: DatabaseAccess) -> bool:
    result = True
    df_forms = get_forms(list(set(df['DateID'])), db_access)
    for d in set(df_forms['DateID']):
        path = df[df['DateID'] == d].iloc[0]['FormPath']
        form = df_forms[df_forms['DateID'] == d].iloc[0]['Form']
        if os.path.exists(path):
            continue
        else:
            try:
                with open(path, 'w',  encoding="utf-8", errors='ignore') as f:
                    f.write(form)
            except Exception as e:
                logging.error(f'ERROR WHILE EXTRACTING FORMS FOR DATEID: {d}')
                result = result and False
                continue
    return result




