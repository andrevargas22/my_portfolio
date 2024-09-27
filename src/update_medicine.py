"""
This script reads a CSV file from a Google Cloud Storage bucket, updates the medication quantities based on the current time, 
and uploads the updated data back to the bucket. It is triggered by GitHub Actions at 10:00 and 22:00 UTC-3.

This is only for personal use and should not be used as a reference for best practices.
"""

import csv
import io
from google.cloud import storage
from datetime import datetime

def update_medications():
    
    # Bucket and blob names
    bucket_name = 'remedios_andre'
    blob_name = 'data_remedios.csv'

    # Connects to the bucket and blob
    client = storage.Client()

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Downloads the CSV file
    conteudo = blob.download_as_text()
    leitor_csv = csv.reader(io.StringIO(conteudo))

    # Reads the CSV file
    headers = [h.strip().lower() for h in next(leitor_csv)]
    dados = []
    for linha in leitor_csv:
        if not linha or len(linha) != len(headers):
            continue
        item = dict(zip(headers, linha))
        dados.append(item)

    # Updates the medication quantities based on the current time
    now = datetime.utcnow()
    hora_local = (now.hour - 3) % 24  # UTC-3
    current_time = now.strftime("%H:%M:%S")
    print("Hora UTC =", current_time)
    print("Hora Local =", f"{hora_local:02d}:{now.minute:02d}:{now.second:02d}")

    if hora_local == 10:
        print("10h update")
        for item in dados:
            if 'n_tacrolimus' in item and 'n_azatioprina' in item:
                item['n_tacrolimus'] = str(int(item['n_tacrolimus']) - 3)
                item['n_azatioprina'] = str(int(item['n_azatioprina']) - 4)
                
    elif hora_local == 22:
        print("22h update")
        for item in dados:
            if 'n_tacrolimus' in item:
                item['n_tacrolimus'] = str(int(item['n_tacrolimus']) - 3)
    else:
        print("Out of update hours")
        return

    # Updates the CSV file
    novo_conteudo = io.StringIO()
    escritor_csv = csv.writer(novo_conteudo)
    escritor_csv.writerow(headers)
    for item in dados:
        linha = [item.get(header, '') for header in headers]
        escritor_csv.writerow(linha)

    blob.upload_from_string(novo_conteudo.getvalue(), content_type='text/csv')

if __name__ == '__main__':
    update_medications()
