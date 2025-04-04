# Guía de Instalación y Uso - AWS SSM Port Forwarding Manager

Esta guía paso a paso te ayudará a instalar y configurar el AWS SSM Port Forwarding Manager para establecer conexiones seguras a recursos privados en AWS.

## Índice

1. [Instalación de requisitos previos](#1-instalación-de-requisitos-previos)
   - [Linux](#11-instalación-en-linux)
   - [Windows](#12-instalación-en-windows)
   - [macOS](#13-instalación-en-macos)
2. [Configuración del script](#2-configuración-del-script)
3. [Creación de tu primera conexión](#3-creación-de-tu-primera-conexión)
4. [Uso de la conexión](#4-uso-de-la-conexión)
5. [Gestión de conexiones](#5-gestión-de-conexiones)
6. [Ejemplos prácticos](#6-ejemplos-prácticos)

## 1. Instalación de requisitos previos

### 1.1 Instalación en Linux

#### Python 3

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Verificar la instalación
python3 --version
```

#### AWS CLI

```bash
# Descargar e instalar AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar la instalación
aws --version
```

#### Plugin de Session Manager

```bash
# Ubuntu/Debian (x86_64)
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb

# Amazon Linux, RHEL, CentOS (x86_64)
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm" -o "session-manager-plugin.rpm"
sudo yum install -y session-manager-plugin.rpm

# Verificar la instalación
session-manager-plugin --version
```

#### Dependencias de Python

```bash
pip3 install boto3 inquirer tabulate cryptography
```

### 1.2 Instalación en Windows

#### Python 3

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Ejecuta el instalador
3. **IMPORTANTE**: Marca la opción "Add Python to PATH" durante la instalación
4. Completa la instalación y verifica en una nueva ventana de PowerShell o CMD:
   ```
   python --version
   ```

#### AWS CLI

1. Descarga el instalador de AWS CLI v2 desde [aws.amazon.com](https://awscli.amazonaws.com/AWSCLIV2.msi)
2. Ejecuta el instalador y sigue las instrucciones
3. Verifica la instalación en una nueva ventana de PowerShell o CMD:
   ```
   aws --version
   ```

#### Plugin de Session Manager

1. Descarga el instalador desde [este enlace](https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe)
2. Ejecuta el instalador y sigue las instrucciones
3. Verifica la instalación en una nueva ventana de PowerShell o CMD:
   ```
   session-manager-plugin --version
   ```

#### Dependencias de Python

Abre PowerShell o CMD y ejecuta:
```
pip install boto3 inquirer tabulate cryptography
```

### 1.3 Instalación en macOS

#### Python 3

```bash
# Usando Homebrew (recomendado)
brew install python3

# Verificar la instalación
python3 --version
```

Si no tienes Homebrew, puedes instalarlo con:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

O descarga Python desde [python.org](https://www.python.org/downloads/macos/).

#### AWS CLI

```bash
# Usando Homebrew
brew install awscli

# Alternativa: Instalación manual
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verificar la instalación
aws --version
```

#### Plugin de Session Manager

```bash
# Descargar e instalar
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/session-manager-plugin.pkg" -o "session-manager-plugin.pkg"
sudo installer -pkg session-manager-plugin.pkg -target /

# Verificar la instalación
session-manager-plugin --version
```

#### Dependencias de Python

```bash
pip3 install boto3 inquirer tabulate cryptography
```

### 1.4 Configuración de AWS CLI

Configura tus credenciales de AWS (esto es igual para todos los sistemas operativos):

```bash
aws configure
# O para un perfil específico
aws configure --profile nombre_perfil
```

Ingresa tu Access Key ID, Secret Access Key, región predeterminada y formato de salida cuando se te solicite.

## 2. Configuración del script

### 2.1 Descarga del script

#### En Linux/macOS

```bash
# Crea un directorio para el script (opcional)
mkdir -p ~/aws-tools
cd ~/aws-tools

# Copia el script a este directorio
cp /ruta/al/script/ssm_port_forwarder.py .

# Haz el script ejecutable
chmod +x ssm_port_forwarder.py
```

#### En Windows

1. Crea una carpeta para el script, por ejemplo en `C:\Users\TuUsuario\aws-tools`
2. Copia el archivo `ssm_port_forwarder.py` a esta carpeta
3. Para ejecutar el script, abre PowerShell o CMD en esa carpeta y usa:
   ```
   python ssm_port_forwarder.py
   ```

### 2.2 Verificación inicial

#### En Linux/macOS

```bash
./ssm_port_forwarder.py --help
```

#### En Windows

```
python ssm_port_forwarder.py --help
```

Deberías ver la ayuda del script con las opciones disponibles.

## 3. Creación de tu primera conexión

### 3.1 Inicia el script en modo interactivo

#### En Linux/macOS

```bash
./ssm_port_forwarder.py
```

#### En Windows

```
python ssm_port_forwarder.py
```

### 3.2 Selecciona "Crear nueva conexión"

Selecciona la opción 1 del menú principal.

### 3.3 Configura la conexión

Sigue los pasos que te solicita el script:

1. **Nombre de la conexión**: Ingresa un nombre descriptivo (ej. "rds-dev-database")
2. **Perfil AWS**: Selecciona el perfil AWS que deseas utilizar
3. **Autenticación**: Si es necesario, el script te guiará para iniciar sesión con SSO
4. **Instancia intermediaria**: Selecciona una instancia EC2 con el agente SSM instalado
5. **Host remoto**: Ingresa la dirección del host al que quieres conectarte (ej. "mi-db.cluster-xyz.us-east-1.rds.amazonaws.com")
6. **Puerto remoto**: Ingresa el puerto del servicio remoto (ej. "5432" para PostgreSQL)
7. **Puerto local**: Ingresa el puerto local que quieres usar (ej. "5439")

### 3.4 Guarda la conexión

El script guardará automáticamente la conexión en un archivo encriptado. La primera vez, te pedirá crear una contraseña para proteger este archivo y te solicitará confirmarla para evitar errores. Esta contraseña será necesaria cada vez que quieras acceder a tus conexiones guardadas.

**Nota importante sobre la seguridad**: El sistema implementa un límite de 3 intentos para ingresar la contraseña correcta. Si ingresas una contraseña incorrecta 3 veces seguidas, el script no cargará las conexiones guardadas.

## 4. Uso de la conexión

### 4.1 Inicia la conexión

Puedes iniciar la conexión de dos formas:

**Desde el menú interactivo:**
```bash
# Linux/macOS
./ssm_port_forwarder.py
# Windows
python ssm_port_forwarder.py

# Selecciona la opción 3 y luego el nombre de tu conexión
```

**Directamente desde la línea de comandos:**
```bash
# Linux/macOS
./ssm_port_forwarder.py --connect "nombre_conexion"
# Windows
python ssm_port_forwarder.py --connect "nombre_conexion"
```

### 4.2 Verifica que la conexión está activa

Verás un mensaje como:
```
Starting port forwarding session...
Local port 5439 → Instance i-0123456789abcdef → Remote mi-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432

Press Ctrl+C to stop the session

Starting session with SessionId: usuario-xyz123
Port 5439 opened for sessionId usuario-xyz123.
Waiting for connections...
```

### 4.3 Conéctate al servicio remoto

Ahora puedes conectarte al servicio remoto a través de localhost:puerto_local.

**Ejemplo para PostgreSQL:**
```bash
psql -h localhost -p 5439 -U usuario -d nombre_base_datos
```

**Ejemplo para MySQL:**
```bash
mysql -h 127.0.0.1 -P 5439 -u usuario -p
```

### 4.4 Finaliza la conexión

Cuando termines, presiona `Ctrl+C` en la terminal donde está ejecutándose el script para finalizar la sesión de port forwarding.

## 5. Gestión de conexiones

### 5.1 Listar conexiones guardadas

```bash
# Linux/macOS
./ssm_port_forwarder.py --list
# Windows
python ssm_port_forwarder.py --list
```

O selecciona la opción 2 en el menú interactivo.

### 5.2 Eliminar una conexión

```bash
# Linux/macOS
./ssm_port_forwarder.py --delete "nombre_conexion"
# Windows
python ssm_port_forwarder.py --delete "nombre_conexion"
```

O selecciona la opción 4 en el menú interactivo.

## 6. Ejemplos prácticos

### 6.1 Conexión a una base de datos RDS PostgreSQL

```bash
# Crear la conexión
./ssm_port_forwarder.py --new  # (o python ssm_port_forwarder.py --new en Windows)
# Nombre: rds-postgres-dev
# Perfil: dev
# Instancia: selecciona una instancia en la misma VPC que la base de datos
# Host remoto: tu-db.cluster-xyz.us-east-1.rds.amazonaws.com
# Puerto remoto: 5432
# Puerto local: 5439

# Conectar usando psql
psql -h localhost -p 5439 -U postgres -d postgres
```

### 6.2 Conexión a un servidor web interno

```bash
# Crear la conexión
./ssm_port_forwarder.py --new  # (o python ssm_port_forwarder.py --new en Windows)
# Nombre: internal-web-app
# Perfil: prod
# Instancia: selecciona una instancia con acceso al servidor web
# Host remoto: internal-web-server.internal
# Puerto remoto: 80
# Puerto local: 8080

# Acceder al servidor web
# Abre tu navegador y visita: http://localhost:8080
```

### 6.3 Conexión a un servidor Redis

```bash
# Crear la conexión
./ssm_port_forwarder.py --new  # (o python ssm_port_forwarder.py --new en Windows)
# Nombre: redis-cache
# Perfil: staging
# Instancia: selecciona una instancia con acceso al servidor Redis
# Host remoto: redis-cluster.internal
# Puerto remoto: 6379
# Puerto local: 6379

# Conectar usando redis-cli
redis-cli -h localhost -p 6379
```

### 6.4 Mantener la conexión en segundo plano

#### En Linux/macOS

Para mantener la conexión activa en segundo plano, puedes usar `screen` o `tmux`:

```bash
# Usando screen
screen -S ssm-tunnel
./ssm_port_forwarder.py --connect "rds-postgres-dev"
# Presiona Ctrl+A, D para desconectar la sesión
# Para volver: screen -r ssm-tunnel

# Usando tmux
tmux new -s ssm-tunnel
./ssm_port_forwarder.py --connect "rds-postgres-dev"
# Presiona Ctrl+B, D para desconectar la sesión
# Para volver: tmux attach -t ssm-tunnel

# Usando nohup
nohup ./ssm_port_forwarder.py --connect "rds-postgres-dev" > tunnel.log 2>&1 &
# Para terminar: encuentra el PID y usa kill
ps aux | grep ssm_port_forwarder
kill <PID>
```

#### En Windows

Para mantener la conexión en segundo plano en Windows, puedes usar:

1. **Windows Terminal** con pestañas
2. **PowerShell como servicio**:
   ```powershell
   Start-Process -NoNewWindow python -ArgumentList "ssm_port_forwarder.py --connect rds-postgres-dev"
   ```
3. **Crear un servicio de Windows** con herramientas como NSSM (Non-Sucking Service Manager)
### 5.3 Cambiar la contraseña

Para cambiar la contraseña que protege tus conexiones guardadas:

```bash
# Linux/macOS
./ssm_port_forwarder.py --change-password
# Windows
python ssm_port_forwarder.py --change-password
```

O selecciona la opción 5 "Change password" en el menú interactivo.

El proceso te pedirá:
1. La contraseña actual para verificar tu identidad
2. La nueva contraseña que deseas usar
3. Confirmación de la nueva contraseña

Una vez completado, todas tus conexiones estarán protegidas con la nueva contraseña.
