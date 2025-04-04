# Permisos IAM para AWS SSM Port Forwarding Manager

Este documento detalla los permisos de AWS Identity and Access Management (IAM) necesarios para utilizar el AWS SSM Port Forwarding Manager de manera efectiva y segura.

## Índice

1. [Permisos para usuarios o roles](#permisos-para-usuarios-o-roles)
   - [Política mínima requerida](#política-mínima-requerida)
   - [Política recomendada para producción](#política-recomendada-para-producción)
   - [Explicación de permisos](#explicación-de-permisos)
2. [Permisos para instancias EC2](#permisos-para-instancias-ec2)
   - [Rol de instancia](#rol-de-instancia)
   - [Política para el rol de instancia](#política-para-el-rol-de-instancia)
3. [Configuración para AWS SSO](#configuración-para-aws-sso)
4. [Verificación de permisos](#verificación-de-permisos)
5. [Solución de problemas comunes](#solución-de-problemas-comunes)
6. [Mejores prácticas de seguridad](#mejores-prácticas-de-seguridad)

## Permisos para usuarios o roles

### Política mínima requerida

La siguiente política IAM contiene los permisos mínimos necesarios para que un usuario o rol pueda utilizar el script de port forwarding:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:StartSession",
                "ssm:TerminateSession",
                "ssm:ResumeSession",
                "ssm:DescribeInstanceInformation",
                "ec2:DescribeInstances",
                "ec2:DescribeTags"
            ],
            "Resource": "*"
        }
    ]
}
```

Esta política permite:
- Iniciar, terminar y reanudar sesiones de SSM
- Listar instancias gestionadas por SSM
- Obtener información sobre instancias EC2 y sus etiquetas

### Política recomendada para producción

Para entornos de producción, se recomienda una política más restrictiva que limite el acceso solo a instancias específicas y a los documentos de SSM necesarios:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeInstanceInformation",
                "ec2:DescribeInstances",
                "ec2:DescribeTags"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:StartSession"
            ],
            "Resource": [
                "arn:aws:ec2:*:*:instance/i-*"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:ResourceTag/SSMAccess": "Enabled"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:StartSession"
            ],
            "Resource": [
                "arn:aws:ssm:*:*:document/AWS-StartPortForwardingSessionToRemoteHost",
                "arn:aws:ssm:*:*:document/AWS-StartPortForwardingSession"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:TerminateSession",
                "ssm:ResumeSession"
            ],
            "Resource": [
                "arn:aws:ssm:*:*:session/${aws:username}-*"
            ]
        }
    ]
}
```

### Explicación de permisos

#### Permisos de SSM

- `ssm:StartSession`: Permite iniciar sesiones de SSM, incluyendo sesiones de port forwarding
- `ssm:TerminateSession`: Permite finalizar sesiones de SSM
- `ssm:ResumeSession`: Permite reanudar sesiones de SSM interrumpidas
- `ssm:DescribeInstanceInformation`: Permite listar instancias gestionadas por SSM

#### Permisos de EC2

- `ec2:DescribeInstances`: Permite obtener información sobre instancias EC2
- `ec2:DescribeTags`: Permite obtener las etiquetas de las instancias EC2

#### Restricciones por etiquetas

La política recomendada incluye una condición que limita el acceso solo a instancias con la etiqueta `SSMAccess: Enabled`. Esto permite un control más granular sobre qué instancias pueden ser utilizadas para port forwarding.

#### Restricciones por documentos de SSM

La política recomendada también limita el acceso solo a los documentos de SSM específicos para port forwarding:
- `AWS-StartPortForwardingSessionToRemoteHost`: Para port forwarding a hosts remotos
- `AWS-StartPortForwardingSession`: Para port forwarding directo a la instancia

#### Restricciones por sesión

La política recomendada limita los permisos para terminar o reanudar sesiones solo a aquellas creadas por el mismo usuario (`${aws:username}-*`).

## Permisos para instancias EC2

### Rol de instancia

Las instancias EC2 que se utilizarán como intermediarias para el port forwarding deben tener un rol de IAM con los permisos necesarios para comunicarse con el servicio SSM.

### Política para el rol de instancia

La política administrada `AmazonSSMManagedInstanceCore` suele ser suficiente para la mayoría de los casos:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeAssociation",
                "ssm:GetDeployablePatchSnapshotForInstance",
                "ssm:GetDocument",
                "ssm:DescribeDocument",
                "ssm:GetManifest",
                "ssm:ListAssociations",
                "ssm:ListInstanceAssociations",
                "ssm:PutInventory",
                "ssm:PutComplianceItems",
                "ssm:PutConfigurePackageResult",
                "ssm:UpdateAssociationStatus",
                "ssm:UpdateInstanceAssociationStatus",
                "ssm:UpdateInstanceInformation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2messages:AcknowledgeMessage",
                "ec2messages:DeleteMessage",
                "ec2messages:FailMessage",
                "ec2messages:GetEndpoint",
                "ec2messages:GetMessages",
                "ec2messages:SendReply"
            ],
            "Resource": "*"
        }
    ]
}
```

Si necesitas permisos adicionales para que la instancia acceda a otros servicios de AWS (como S3, CloudWatch, etc.), deberás añadirlos al rol de la instancia.

## Configuración para AWS SSO

Si utilizas AWS SSO (Single Sign-On), necesitarás asegurarte de que el conjunto de permisos (permission set) asignado a tu usuario incluya los permisos mencionados anteriormente.

### Pasos para configurar permisos en AWS SSO

1. Inicia sesión en la consola de AWS como administrador
2. Ve a AWS SSO
3. Selecciona "Conjuntos de permisos"
4. Crea un nuevo conjunto de permisos o edita uno existente
5. Añade una política en línea con los permisos necesarios
6. Asigna este conjunto de permisos a los usuarios o grupos que necesiten usar el script

## Verificación de permisos

Puedes verificar si tienes los permisos necesarios ejecutando los siguientes comandos:

```bash
# Verificar identidad
aws sts get-caller-identity --profile tu_perfil

# Verificar acceso a SSM
aws ssm describe-instance-information --profile tu_perfil

# Verificar acceso a EC2
aws ec2 describe-instances --profile tu_perfil --filters "Name=tag:SSMAccess,Values=Enabled" --query "Reservations[].Instances[].InstanceId"
```

Si estos comandos se ejecutan correctamente, probablemente tengas los permisos básicos necesarios para usar el script.

## Solución de problemas comunes

### Error: "User is not authorized to perform: ssm:StartSession"

**Problema**: No tienes permisos para iniciar sesiones de SSM.

**Solución**: Asegúrate de que tu usuario o rol tenga el permiso `ssm:StartSession` y que esté correctamente configurado para los recursos específicos (instancias y documentos de SSM).

### Error: "An error occurred (AccessDeniedException) when calling the DescribeInstanceInformation operation"

**Problema**: No tienes permisos para listar instancias gestionadas por SSM.

**Solución**: Asegúrate de que tu usuario o rol tenga el permiso `ssm:DescribeInstanceInformation`.

### Error: "An error occurred (AccessDeniedException) when calling the DescribeInstances operation"

**Problema**: No tienes permisos para obtener información sobre instancias EC2.

**Solución**: Asegúrate de que tu usuario o rol tenga el permiso `ec2:DescribeInstances`.

### No se muestran instancias en el script

**Problema**: El script no muestra ninguna instancia al crear una conexión.

**Solución**:
1. Verifica que las instancias tengan el agente SSM instalado y estén en estado "Online"
2. Asegúrate de que las instancias tengan las etiquetas necesarias si estás usando restricciones por etiquetas
3. Verifica que estás usando la región correcta en tu perfil AWS

## Mejores prácticas de seguridad

### 1. Principio de privilegio mínimo

Sigue el principio de privilegio mínimo, otorgando solo los permisos necesarios para realizar las tareas requeridas. Utiliza la política recomendada para producción que incluye restricciones por etiquetas y documentos de SSM.

### 2. Uso de etiquetas para control de acceso

Utiliza etiquetas (como `SSMAccess: Enabled`) para controlar qué instancias pueden ser utilizadas para port forwarding. Esto te permite un control más granular y evita el acceso no autorizado a instancias críticas.

### 3. Rotación de credenciales

Si utilizas credenciales de larga duración (access key y secret key), asegúrate de rotarlas regularmente. Mejor aún, utiliza AWS SSO o roles temporales siempre que sea posible.

### 4. Monitoreo y auditoría

Habilita AWS CloudTrail para registrar todas las llamadas a la API de AWS, incluyendo las sesiones de SSM. Esto te permitirá auditar quién ha iniciado sesiones de port forwarding y cuándo.

### 5. Uso de VPC Endpoints para SSM

Considera utilizar VPC Endpoints para SSM para que las instancias no necesiten acceso a internet para comunicarse con el servicio SSM. Esto mejora la seguridad al reducir la superficie de ataque.

### 6. Restricción por dirección IP

Considera añadir condiciones adicionales en las políticas IAM para restringir el acceso por dirección IP, permitiendo iniciar sesiones de SSM solo desde rangos de IP específicos.

```json
"Condition": {
    "IpAddress": {
        "aws:SourceIp": [
            "192.168.1.0/24",
            "203.0.113.0/24"
        ]
    }
}
```

### 7. Restricción por tiempo

Puedes añadir condiciones temporales para permitir el acceso solo durante horarios laborales:

```json
"Condition": {
    "DateGreaterThan": {"aws:CurrentTime": "2023-01-01T08:00:00Z"},
    "DateLessThan": {"aws:CurrentTime": "2023-01-01T18:00:00Z"}
}
```

### 8. Seguridad de las conexiones guardadas

El script implementa varias medidas para proteger las conexiones guardadas:

- **Encriptación fuerte**: Utiliza Fernet (AES-128) para encriptar el archivo de conexiones
- **Derivación segura de claves**: Usa PBKDF2 con 100,000 iteraciones y un salt único
- **Confirmación de contraseña**: Solicita confirmación al crear una nueva contraseña
- **Protección contra ataques de fuerza bruta**: Limita a 3 los intentos de contraseña incorrecta
- **Validación de contraseña**: No permite contraseñas vacías
