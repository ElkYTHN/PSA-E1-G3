import socket
import mysql.connector
from datetime import datetime

IP = socket.gethostname()
#IP = "192.168.229.134"
PORT = 8888

# Creación del socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen()
print('Servidor de pagos de agua iniciado. Esperando conexiones...')


# Conexión a la base de datos
db = mysql.connector.connect(
  host='localhost',
  user='root',
  password='',
  database='pago_agua'
)

#Logica de los pagos de los clientes
while True:
  client_socket, address = server_socket.accept()
  print(f'Cliente conectado desde {address}')


  # Recibir el número de cliente
  client_id = client_socket.recv(1024).decode('utf-8')


  # Buscar al cliente en la base de datos
  cursor = db.cursor()
  cursor.execute(f"SELECT * FROM clientes WHERE id = '{client_id}'")
  client_data = cursor.fetchone()
  
  if not client_data:
    # Si el cliente no existe, preguntar si desea registrarse
    client_socket.sendall('El cliente no existe. ¿Desea registrarse? (S/N) '.encode('utf-8'))
    register = client_socket.recv(1024).decode('utf-8')


    if register.upper() == 'S':
      # Si el cliente desea registrarse, pedir su nombre y saldo inicial
      client_socket.sendall('Ingrese su nombre: '.encode('utf-8'))
      client_name = client_socket.recv(1024).decode('utf-8')
      client_socket.sendall('Ingrese su saldo inicial: '.encode('utf-8'))
      client_balance = float(client_socket.recv(1024).decode('utf-8'))


      # Insertar al nuevo cliente en la base de datos
      cursor.execute(f"INSERT INTO clientes VALUES ('{client_id}', '{client_name}', {client_balance})")
      db.commit()
      client_socket.sendall('Registro exitoso.'.encode('utf-8'))
    else:
      client_socket.sendall('Adiós.'.encode('utf-8'))
  else:

    # Si el cliente existe, mostrar su saldo actual y pedir la cantidad a pagar
    client_socket.sendall(f'Su saldo actual es {client_data[2]:.2f}. Ingrese la cantidad a pagar: '.encode('utf-8'))
    payment = float(client_socket.recv(1024).decode('utf-8'))

    if payment <= 0 or payment > client_data[2]:
      # Si la cantidad a pagar es inválida, mostrar un mensaje de error
      client_socket.sendall('La cantidad ingresada es inválida.'.encode('utf-8'))

    else:

      # Si la cantidad a pagar es válida, actualizar el saldo del cliente en la base de datos
      now = datetime.now()
      cursor.execute(f"INSERT INTO pagos (cliente_id, fecha_hora, pago) VALUES ('{client_id}', '{now}', {payment})")
      new_balance = client_data[2] - payment
      cursor.execute(f"UPDATE clientes SET saldo = {new_balance:.2f} WHERE id = '{client_id}'")
      db.commit()
      client_socket.sendall(f'Su nuevo saldo es de {new_balance:.2f}. Pago realizado correctamente.'.encode('utf-8'))

      # Esperar por una posible reversión del pago
      revert = client_socket.recv(1024).decode('utf-8')

      if revert.upper() == 'S':
        # Si se solicita una reversión del pago, restaurar el saldo anterior
        cursor.execute(f"UPDATE clientes SET saldo = {client_data[2]:.2f} WHERE id = '{client_id}'")
        cursor.execute(f"DELETE FROM pagos ORDER BY id DESC LIMIT 1")
        db.commit()
        client_socket.sendall(f'Se ha restaurado su saldo anterior de {client_data[2]:.2f}.'.encode('utf-8'))
      else:
        client_socket.sendall('Gracias por su pago.'.encode('utf-8'))

        client_socket.close()


  #Historial de Pagos
  history_socket, address = server_socket.accept()
  #if opcion == 'H':
  # recibir el número de cliente enviado por el cliente
  cliente = history_socket.recv(1024).decode('utf-8')
  cursor = db.cursor()
  # consultar la base de datos para obtener los registros de pagos del cliente
  cursor.execute("SELECT fecha_hora, pago FROM pagos WHERE cliente_id = %s", (cliente,))
  pagos = cursor.fetchall()
  # preparar la respuesta para enviar al cliente
  if pagos:
      respuesta = "Historial de pagos:\n"
      for pago in pagos:
          respuesta += "- Fecha: " + str(pago[0]) + " - Monto: " + str(pago[1]) + "\n"
  else:
      respuesta = "No se encontraron registros de pagos para este cliente."
  # enviar la respuesta al cliente
  history_socket.send(respuesta.encode('utf-8'))
  history_socket.close()

db.close()



