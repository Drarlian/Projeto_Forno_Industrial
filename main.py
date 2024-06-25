from datetime import datetime

import aiofiles
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


class Informations(BaseModel):
    temperature_ini: str
    temperature_mid: str
    temperature_end: str
    pressure: str
    speed: str
    work_on: str
    work_off: str
    message_system: str


@app.get('/')
def home():
    return {"Nome": "Informações do Forno Industrial"}


@app.post("/receive-data")
async def receive_data(request: Request):
    data = await request.json()

    if change_temperature(data['temperature_end']) > 100:
        await send_email(data['temperature_end'])

    print(datetime.now())
    return {"message": "Dados recebidos com sucesso"}


async def get_credencials():

    async with aiofiles.open('credencials.txt', 'r') as infos:
        new_infos = await infos.readlines()
        infos_emails = new_infos[0].replace('\n', '').split('=')[1]
        infos_senha = new_infos[1].split('=')[1]
        infos_destino = new_infos[2].split('=')[1]

    return {
        'infos_emails': infos_emails,
        'infos_senha': infos_senha,
        'infos_destino': infos_destino
    }


async def send_email(temperature: float):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    basic_infos = await get_credencials()

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email = basic_infos['infos_emails']
    password = basic_infos['infos_senha']

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = basic_infos['infos_destino']
    msg['Subject'] = "Temperatura Alta!"

    temperature = change_temperature(temperature)
    corpo_html = f"""
    <html>
    <head></head>
    <body>
        <h1>Alerta de Temperatura Alta no Forno Industrial</h1>
        <p>
            Esse e-mail está sendo enviado pois o Forno Industrial alcançou uma temperatura <b>muito alta</b>!
        </p>
        <p>Temperatura atual: {temperature}Cº</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(corpo_html, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        server.login(email, password)

        server.sendmail(email, msg['To'], msg.as_string())
        print("E-mail enviado com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    else:
        server.quit()


def change_temperature(value: float):
    celsius = (value - 32) * 5.0 / 9.0
    return celsius


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
