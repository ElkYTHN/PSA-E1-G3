import socket

IP = socket.gethostname()
#IP = "192.168.229.134"
PORT = 8888

#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket.connect((IP, PORT))

while True:
    print("Bienvenido al Sistema de Pagos de Agua")
    print("1. Realizar Pago")
    print("2. Consulta Historial de Pagos")
    print("3. Consulta de Saldo")
    print("4. Salir")

    opcion = input("Selecciona una opcion: ")

    #Hacer los pagos
    if opcion == "1":

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))

        client_id = input('Ingrese su número de cliente: ')
        client_socket.sendall(client_id.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')

        if response.startswith('El cliente no existe'):
            register = input(response)
            client_socket.sendall(register.encode('utf-8'))

            if register.upper() == 'S':

                client_name = input(client_socket.recv(1024).decode('utf-8'))
                client_socket.sendall(client_name.encode('utf-8'))
                client_balance = input(client_socket.recv(1024).decode('utf-8'))
                client_socket.sendall(client_balance.encode('utf-8'))

                # Recibir la confirmación del registro
                response = client_socket.recv(1024).decode('utf-8')
                print(response)
            else:
                print(client_socket.recv(1024).decode('utf-8'))
        else:
            # Si el cliente existe, mostrar su saldo actual y pedir la cantidad a pagar
            payment = float(input(response))
            client_socket.sendall(str(payment).encode('utf-8'))

            # Recibir la respuesta del servidor
            response = client_socket.recv(1024).decode('utf-8')

            if response.startswith('La cantidad ingresada es inválida'):
                print(response)
            else:
                print(response)
                revert = input('¿Desea revertir el pago? (S/N) ')
                client_socket.sendall(revert.encode('utf-8'))

                # Recibir la respuesta del servidor
                response = client_socket.recv(1024).decode('utf-8')

                if revert.upper() == 'S':
                # Si se solicita una reversión del pago, mostrar el saldo anterior
                    print(response)
                else:
                # Si no se solicita una reversión del pago, mostrar un mensaje de confirmación
                    print(response)
                client_socket.close()
                break

    #Consulta de Historial de pagos            
    elif opcion == "2":
        history_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        history_socket.connect((IP, PORT))
        # solicitar el número de cliente al usuario
        cliente = input("Ingrese el número de cliente: ")
        # enviar el número de cliente al servidor para consultar el historial de pagos
        history_socket.send(cliente.encode('utf-8'))
        # recibir la respuesta del servidor
        respuesta = history_socket.recv(1024).decode('utf-8')
        # mostrar la respuesta en pantalla
        print(respuesta)
        #del opcion
        break

    elif opcion == "3":
        print("Has seleccionado la opción 2")

    elif opcion == "4":
        exit(print("¡Gracias por usar nuestro sistema!"))
        
    else:
        print("Opción inválida. Inténtalo de nuevo.")
