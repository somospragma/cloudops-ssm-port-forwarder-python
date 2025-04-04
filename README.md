# AWS SSM Port Forwarding Manager

Este script facilita la creación y gestión de conexiones de port forwarding seguras utilizando AWS Systems Manager (SSM), permitiéndote acceder a recursos privados en AWS sin necesidad de exponer puertos públicamente o mantener un host bastión dedicado.

## Documentación Completa

Este repositorio contiene varios documentos para ayudarte a entender y utilizar el AWS SSM Port Forwarding Manager:

1. **[README.md](README.md)** (este archivo) - Visión general y uso básico
2. **[GUIA_INSTALACION.md](GUIA_INSTALACION.md)** - Instrucciones detalladas de instalación para Linux, Windows y macOS
3. **[EXPLICACION_CODIGO.md](EXPLICACION_CODIGO.md)** - Explicación técnica del funcionamiento interno del script
4. **[PERMISOS_IAM.md](PERMISOS_IAM.md)** - Guía completa de permisos AWS IAM y consideraciones de seguridad

## Índice

- [Descripción](#descripción)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso del script](#uso-del-script)
  - [Modo interactivo](#modo-interactivo)
  - [Comandos disponibles](#comandos-disponibles)
- [Flujo de trabajo típico](#flujo-de-trabajo-típico)
- [Explicación detallada de funcionalidades](#explicación-detallada-de-funcionalidades)
- [Seguridad](#seguridad)
- [Solución de problemas](#solución-de-problemas)
- [Preguntas frecuentes](#preguntas-frecuentes)

## Descripción

AWS SSM Port Forwarding Manager es una herramienta que simplifica el proceso de establecer túneles seguros a recursos privados en AWS (como bases de datos RDS, instancias EC2 en subredes privadas, etc.) utilizando el servicio AWS Systems Manager Session Manager.

La herramienta permite:

- Crear y guardar configuraciones de conexión
- Gestionar perfiles de AWS y sesiones de SSO
- Seleccionar instancias intermediarias con el agente SSM instalado
- Establecer túneles seguros a hosts remotos
- Almacenar las configuraciones de forma encriptada

## Requisitos previos

Para utilizar este script necesitas:

1. **Python 3.6 o superior** instalado en tu sistema
2. **AWS CLI** configurado con credenciales válidas
3. **Plugin de Session Manager para AWS CLI** instalado
4. **Al menos una instancia EC2** con el agente SSM instalado y configurado
5. **Permisos IAM** adecuados para usar SSM Session Manager

### Verificación de requisitos

1. Verifica la versión de Python:
   ```bash
   python3 --version
   ```

2. Verifica que AWS CLI está instalado:
   ```bash
   aws --version
   ```

3. Verifica que el plugin de Session Manager está instalado:
   ```bash
   session-manager-plugin --version
   ```

4. Verifica que tienes instancias gestionadas por SSM:
   ```bash
   aws ssm describe-instance-information
   ```

## Instalación

1. **Instala las dependencias necesarias**:

   ```bash
   pip install boto3 inquirer tabulate cryptography
   ```

2. **Descarga el script**:

   ```bash
   # Clona el repositorio o copia el script directamente
   chmod +x ssm_port_forwarder.py
   ```

3. **Verifica la instalación**:

   ```bash
   ./ssm_port_forwarder.py --help
   ```

## Uso del script

### Modo interactivo

La forma más sencilla de usar el script es en modo interactivo:

```bash
./ssm_port_forwarder.py
```

Esto mostrará un menú con las siguientes opciones:
1. Crear nueva conexión
2. Listar conexiones guardadas
3. Conectar usando una conexión guardada
4. Eliminar conexión
5. Salir

### Comandos disponibles

También puedes usar el script con argumentos de línea de comandos:

```bash
# Crear una nueva conexión
./ssm_port_forwarder.py --new

# Listar conexiones guardadas
./ssm_port_forwarder.py --list

# Conectar usando una conexión guardada
./ssm_port_forwarder.py --connect "nombre_conexion"

# Eliminar una conexión guardada
./ssm_port_forwarder.py --delete "nombre_conexion"
```

## Flujo de trabajo típico

### 1. Crear una nueva conexión

Al crear una nueva conexión, el script te guiará a través de los siguientes pasos:

1. **Nombre de la conexión**: Asigna un nombre descriptivo a la conexión
2. **Selección de perfil AWS**: Elige el perfil AWS a utilizar
3. **Autenticación SSO** (si es necesario): El script verificará si necesitas iniciar sesión con SSO
4. **Selección de instancia intermediaria**: Elige una instancia EC2 con el agente SSM instalado
5. **Configuración del host remoto**:
   - Dirección IP o nombre del host remoto
   - Puerto remoto al que quieres conectarte
   - Puerto local que quieres usar para la conexión

### 2. Iniciar una conexión

Al iniciar una conexión:

1. El script establece un túnel seguro a través de SSM
2. El puerto local especificado se abre en tu máquina
3. Todo el tráfico a ese puerto local se reenvía al puerto remoto del host destino
4. La sesión permanece activa hasta que presiones Ctrl+C

### 3. Usar la conexión

Una vez establecida la conexión, puedes usar cualquier cliente para conectarte al servicio remoto a través de `localhost:puerto_local`. Por ejemplo:

- Para una base de datos MySQL/PostgreSQL: Usa tu cliente SQL favorito
- Para un servidor web: Abre tu navegador y visita `http://localhost:puerto_local`

## Explicación detallada de funcionalidades

### Gestión de perfiles AWS

El script detecta automáticamente los perfiles AWS configurados en tu sistema, buscando en:
- `~/.aws/credentials`
- `~/.aws/config`

Esto te permite seleccionar fácilmente el perfil adecuado para cada conexión.

### Autenticación SSO

Si utilizas AWS SSO, el script:
1. Verifica si tu sesión SSO está activa
2. Si la sesión ha expirado, inicia automáticamente el proceso de login
3. Continúa con la operación una vez que la autenticación es exitosa

### Selección de instancias

El script muestra una lista de todas las instancias gestionadas por SSM que están en estado "Online", mostrando:
- Nombre de la instancia (tag "Name")
- ID de la instancia
- Dirección IP

### Gestión de contraseñas

El script proporciona funcionalidades para gestionar la contraseña de encriptación:

1. **Cambio de contraseña**: Puedes cambiar la contraseña en cualquier momento usando la opción "Change password" en el menú o el parámetro `--change-password` en la línea de comandos.
2. **Confirmación de contraseña**: Al crear o cambiar una contraseña, se solicita confirmación para evitar errores.
3. **Validación de contraseña**: No se permiten contraseñas vacías.
4. **Límite de intentos**: Se permiten hasta 3 intentos para ingresar la contraseña correcta.

### Comandos SSM utilizados

El script utiliza el siguiente comando de AWS CLI para establecer el port forwarding:

```bash
aws ssm start-session \
  --profile <perfil> \
  --target <id-instancia> \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"portNumber":["<puerto-remoto>"],"localPortNumber":["<puerto-local>"],"host":["<host-remoto>"]}'
```

## Seguridad

### Consideraciones de seguridad

1. **Credenciales AWS**: El script no almacena tus credenciales AWS, utiliza los perfiles configurados en tu sistema
2. **Contraseña de encriptación**: La contraseña para encriptar las conexiones no se guarda, solo se usa un salt para la derivación de la clave
3. **Conexiones seguras**: Todo el tráfico va a través de AWS SSM, que utiliza TLS para encriptar las comunicaciones
4. **Sin puertos expuestos**: No es necesario abrir puertos en firewalls o grupos de seguridad

### Mejores prácticas

1. Usa una contraseña fuerte para encriptar el archivo de conexiones
2. Asegúrate de que tus instancias EC2 tengan solo los permisos mínimos necesarios
3. Considera usar roles IAM temporales para acceder a AWS
4. Cierra las sesiones de port forwarding cuando no las necesites

## Solución de problemas

### Problemas comunes

#### No se pueden listar instancias SSM

**Problema**: El script no muestra ninguna instancia al crear una conexión.

**Solución**:
1. Verifica que tienes permisos para listar instancias SSM:
   ```bash
   aws ssm describe-instance-information --profile tu_perfil
   ```
2. Asegúrate de que las instancias tienen el agente SSM instalado y están en estado "Online"
3. Verifica que estás usando la región correcta en tu perfil AWS

#### Error de autenticación

**Problema**: Aparecen errores relacionados con credenciales o permisos.

**Solución**:
1. Verifica que tu perfil AWS está correctamente configurado:
   ```bash
   aws sts get-caller-identity --profile tu_perfil
   ```
2. Si usas SSO, asegúrate de que tu sesión no ha expirado:
   ```bash
   aws sso login --profile tu_perfil
   ```
3. Verifica que tienes los permisos IAM necesarios para usar SSM Session Manager

#### La conexión se establece pero no puedo conectarme al servicio

**Problema**: El túnel SSM se establece correctamente pero no puedes conectarte al servicio remoto.

**Solución**:
1. Verifica que el host remoto es accesible desde la instancia intermediaria:
   ```bash
   aws ssm start-session --target tu_instancia_id
   # Una vez conectado a la instancia:
   ping host_remoto
   telnet host_remoto puerto
   ```
2. Asegúrate de que los grupos de seguridad o firewalls permiten el tráfico desde la instancia intermediaria al host remoto
3. Verifica que estás usando el puerto correcto para el servicio remoto

## Preguntas frecuentes

### ¿Puedo usar este script para conectarme directamente a un servicio AWS sin una instancia EC2?

No, AWS SSM Session Manager siempre requiere una instancia EC2 (u otro recurso) con el agente SSM instalado como intermediario. No es posible establecer un túnel directo a servicios como RDS sin pasar por una instancia EC2.

### ¿Qué permisos IAM necesito para usar este script?

Como mínimo, necesitas:
- `ssm:StartSession`
- `ssm:TerminateSession`
- `ssm:ResumeSession`
- `ec2:DescribeInstances` (para listar instancias)
- `ssm:DescribeInstanceInformation`

### ¿Puedo mantener la conexión activa en segundo plano?

Sí, puedes usar herramientas como `screen`, `tmux` o `nohup` para mantener el script ejecutándose en segundo plano:

```bash
# Usando screen
screen -S ssm-tunnel
./ssm_port_forwarder.py --connect "mi_conexion"
# Presiona Ctrl+A, D para desconectar la sesión
# Para volver: screen -r ssm-tunnel

# Usando nohup
nohup ./ssm_port_forwarder.py --connect "mi_conexion" > tunnel.log 2>&1 
# Para terminar: encuentra el PID y usa kill
```

### ¿Es seguro usar este método para conectarse a bases de datos de producción?

Sí, este método es seguro ya que:
1. No expone puertos públicamente
2. Utiliza la infraestructura segura de AWS SSM
3. Todo el tráfico está encriptado con TLS
4. No requiere almacenar credenciales adicionales

Sin embargo, siempre debes seguir las políticas de seguridad de tu organización y usar este método solo cuando sea necesario.

### ¿Puedo conectarme a múltiples servicios simultáneamente?

Sí, puedes ejecutar múltiples instancias del script para establecer diferentes túneles simultáneamente. Asegúrate de usar diferentes puertos locales para cada conexión.
### Almacenamiento seguro

Las conexiones se guardan en un archivo JSON encriptado (`~/.ssm-port-forwarder/connections.enc`) utilizando:
1. Una contraseña que proporcionas la primera vez (con confirmación)
2. Encriptación Fernet (implementación de AES-128 en CBC mode con PKCS7 padding)
3. Derivación de clave segura con PBKDF2
4. Sistema de protección con límite de 3 intentos de contraseña incorrecta
