from google.cloud import storage
import csv
import io
from datetime import datetime

def update_medications():
    
    # Nome do bucket e arquivo CSV
    bucket_name = 'remedios_andre'
    blob_name = 'data_remedios.csv'

    # Inicializa o cliente do GCS usando as credenciais do arquivo JSON
    #credentials_path = 'cred.json'
    #client = storage.Client.from_service_account_json(credentials_path)
    
    client = storage.Client()
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Faz o download do conteúdo do CSV
    conteudo = blob.download_as_text()
    leitor_csv = csv.reader(io.StringIO(conteudo))

    # Lê o cabeçalho e os dados
    headers = [h.strip().lower() for h in next(leitor_csv)]
    dados = []
    for linha in leitor_csv:
        if not linha or len(linha) != len(headers):
            continue
        item = dict(zip(headers, linha))
        dados.append(item)

    # Checa horário
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    
    if current_time >= "09:00:00" and current_time <= "11:00:00":
        
        # Diminui a quantidade de Tacrolimus em 3 e de Azatioprina em 4, e atualiza o CSV
        for item in dados:
            if 'n_tacrolimus' in item and 'n_azatioprina' in item:
                item['n_tacrolimus'] = str(int(item['n_tacrolimus']) - 3)
                item['n_azatioprina'] = str(int(item['n_azatioprina']) - 4)
            
        # Atualiza o arquivo no GCS
        novo_conteudo = io.StringIO()
        escritor_csv = csv.writer(novo_conteudo)
        escritor_csv.writerow(headers)
        for item in dados:
            linha = [item.get(header, '') for header in headers]
            escritor_csv.writerow(linha)
            
        blob.upload_from_string(novo_conteudo.getvalue(), content_type='text/csv')
        print("Dados atualizados")
    
    elif current_time >= "21:00:00" and current_time <= "23:00:00":
        
        # Diminui apenas a quantidade de Tacrolimus em 3
        for item in dados:
            if 'n_tacrolimus' in item:
                item['n_tacrolimus'] = str(int(item['n_tacrolimus']) - 3)
                
        # Atualiza o arquivo no GCS
        novo_conteudo = io.StringIO()
        escritor_csv = csv.writer(novo_conteudo)
        escritor_csv.writerow(headers)
        for item in dados:
            linha = [item.get(header, '') for header in headers]
            escritor_csv.writerow(linha)
        
        blob.upload_from_string(novo_conteudo.getvalue(), content_type='text/csv')
        
    else:
        print("Fora do horário de atualização")

if __name__ == '__main__':
    update_medications()
