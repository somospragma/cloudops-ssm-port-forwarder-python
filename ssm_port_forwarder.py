#!/usr/bin/env python3
import os
import json
import subprocess
import argparse
import getpass
import base64
import time
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import boto3
import inquirer
from tabulate import tabulate
from pathlib import Path

class SSMPortForwarder:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.ssm-port-forwarder")
        self.connections_file = os.path.join(self.config_dir, "connections.enc")
        self.key_file = os.path.join(self.config_dir, "key.salt")
        self.connections = {}
        self.ensure_config_dir()
        
    def ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
    def get_encryption_key(self, password=None):
        """Get or create encryption key based on password"""
        if not password:
            if os.path.exists(self.key_file):
                try:
                    with open(self.key_file, 'rb') as f:
                        salt = f.read()
                    password = getpass.getpass("Enter password to decrypt connections: ")
                except Exception as e:
                    print(f"Error reading key file: {e}")
                    salt = os.urandom(16)
                    password = getpass.getpass("Create a password to encrypt connections: ")
                    with open(self.key_file, 'wb') as f:
                        f.write(salt)
            else:
                salt = os.urandom(16)
                password = getpass.getpass("Create a password to encrypt connections: ")
                with open(self.key_file, 'wb') as f:
                    f.write(salt)
        else:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    salt = f.read()
            else:
                salt = os.urandom(16)
                with open(self.key_file, 'wb') as f:
                    f.write(salt)
                
        # Asegurarse de que la contraseña no esté vacía
        if not password or password.strip() == "":
            raise ValueError("La contraseña no puede estar vacía")
                
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
        
    def load_connections(self):
        """Load saved connections from encrypted file"""
        if not os.path.exists(self.connections_file):
            self.connections = {}
            return
            
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                key = self.get_encryption_key()
                fernet = Fernet(key)
                
                with open(self.connections_file, 'rb') as f:
                    encrypted_data = f.read()
                    
                decrypted_data = fernet.decrypt(encrypted_data)
                self.connections = json.loads(decrypted_data.decode())
                print(f"Loaded {len(self.connections)} saved connections")
                return
            except (InvalidToken, ValueError) as e:
                attempts += 1
                if attempts < max_attempts:
                    print(f"Error: Contraseña incorrecta. Intento {attempts} de {max_attempts}")
                else:
                    print("Error: Demasiados intentos fallidos. No se pudieron cargar las conexiones.")
            except Exception as e:
                print(f"Error loading connections: {e}")
                break
                
        self.connections = {}
            
    def save_connections(self):
        """Save connections to encrypted file"""
        try:
            # Si es la primera vez que se guarda, solicitar confirmación de contraseña
            if not os.path.exists(self.connections_file):
                password = getpass.getpass("Create a password to encrypt connections: ")
                if not password or password.strip() == "":
                    print("Error: La contraseña no puede estar vacía")
                    return
                    
                confirm_password = getpass.getpass("Confirm password: ")
                if password != confirm_password:
                    print("Error: Las contraseñas no coinciden")
                    return
                
                key = self.get_encryption_key(password)
            else:
                key = self.get_encryption_key()
                
            fernet = Fernet(key)
            
            encrypted_data = fernet.encrypt(json.dumps(self.connections).encode())
            
            with open(self.connections_file, 'wb') as f:
                f.write(encrypted_data)
                
            print(f"Saved {len(self.connections)} connections")
        except Exception as e:
            print(f"Error saving connections: {e}")
            
    def get_aws_profiles(self):
        """Get available AWS profiles"""
        profiles = []
        
        # Check ~/.aws/credentials
        credentials_path = os.path.expanduser("~/.aws/credentials")
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('[') and line.strip().endswith(']'):
                        profile = line.strip()[1:-1]
                        if profile != 'default' and profile not in profiles:
                            profiles.append(profile)
        
        # Check ~/.aws/config for SSO profiles
        config_path = os.path.expanduser("~/.aws/config")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('[profile '):
                        profile = line.strip()[9:-1]
                        if profile not in profiles:
                            profiles.append(profile)
        
        # Add default profile
        if 'default' not in profiles:
            profiles.insert(0, 'default')
        else:
            profiles.remove('default')
            profiles.insert(0, 'default')
            
        return profiles
        
    def check_sso_login(self, profile):
        """Check if SSO login is needed and perform login if necessary"""
        # Validar que el perfil solo contiene caracteres permitidos
        import re
        import webbrowser
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', profile):
            print(f"ERROR: Invalid profile name: {profile}")
            return False
            
        try:
            # Usar lista de argumentos en lugar de shell=True
            cmd = ["aws", "sts", "get-caller-identity", "--profile", profile]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            print("\n" + "=" * 70)
            print(f"ERROR: You are not logged in with AWS SSO profile '{profile}'")
            print(f"\nTo continue, please run this command in your terminal and follow the prompts:")
            print(f"\n    aws sso login --profile {profile}")
            print("\nAfter successful login, run this script again.")
            print("=" * 70 + "\n")
            
            # Opcionalmente, preguntar si desea abrir un navegador para SSO
            try:
                response = input("Would you like to open the AWS SSO login page now? (y/n): ")
                if response.lower() == 'y':
                    print("Opening AWS SSO login page...")
                    # Usar webbrowser para abrir la página de login (más seguro que ejecutar comandos)
                    webbrowser.open("https://signin.aws.amazon.com/signin")
            except Exception as e:
                print(f"Error opening browser: {e}")
                
            return False
                
    def get_ssm_instances(self, profile):
        """Get instances managed by SSM"""
        # Create boto3 session with specified profile
        session = boto3.Session(profile_name=profile)
        ssm_client = session.client('ssm')
        ec2_client = session.client('ec2')
        
        # Get instances managed by SSM
        instances = []
        try:
            response = ssm_client.describe_instance_information()
            
            for instance in response['InstanceInformationList']:
                instance_id = instance['InstanceId']
                status = instance['PingStatus']
                
                # Skip instances that are not online
                if status != 'Online':
                    continue
                    
                # Get instance details from EC2
                try:
                    ec2_response = ec2_client.describe_instances(InstanceIds=[instance_id])
                    ec2_instance = ec2_response['Reservations'][0]['Instances'][0]
                    
                    # Get instance name from tags
                    name = instance_id
                    for tag in ec2_instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                            
                    # Get private IP
                    private_ip = ec2_instance.get('PrivateIpAddress', 'N/A')
                    
                    instances.append({
                        'id': instance_id,
                        'name': name,
                        'ip': private_ip,
                        'status': status
                    })
                except Exception as e:
                    print(f"Error getting EC2 details for instance {instance_id}: {e}")
                    
            return instances
        except Exception as e:
            print(f"Error getting SSM instances: {e}")
            return []
            
    def start_port_forwarding(self, connection):
        """Start port forwarding session"""
        profile = connection['profile']
        instance_id = connection['instance_id']
        remote_host = connection['remote_host']
        remote_port = connection['remote_port']
        local_port = connection['local_port']
        
        # Check SSO login if needed
        if not self.check_sso_login(profile):
            print(f"Failed to authenticate with profile '{profile}'")
            return
            
        # Start port forwarding session
        cmd = (
            f"aws ssm start-session "
            f"--profile {profile} "
            f"--target {instance_id} "
            f"--document-name AWS-StartPortForwardingSessionToRemoteHost "
            f"--parameters '{{\"host\":[\"{remote_host}\"],\"portNumber\":[\"{remote_port}\"],\"localPortNumber\":[\"{local_port}\"]}}'")
            
        print(f"Starting port forwarding session...")
        print(f"Local port {local_port} → Instance {instance_id} → Remote {remote_host}:{remote_port}")
        print("\nPress Ctrl+C to stop the session\n")
        
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error starting port forwarding session: {e}")
        except KeyboardInterrupt:
            print("\nStopping port forwarding session...")
            
    def create_new_connection(self):
        """Create a new connection configuration"""
        # Get available AWS profiles
        profiles = self.get_aws_profiles()
        
        if not profiles:
            print("No AWS profiles found. Please configure AWS CLI first.")
            return None
            
        # Ask for connection name
        name = input("Enter a name for this connection: ")
        if not name:
            print("Connection name cannot be empty")
            return None
            
        if name in self.connections:
            overwrite = input(f"Connection '{name}' already exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                return None
                
        # Ask for AWS profile
        print("\nAvailable AWS profiles:")
        for i, profile in enumerate(profiles):
            print(f"{i+1}. {profile}")
            
        profile_idx = int(input("\nSelect profile (number): ")) - 1
        if profile_idx < 0 or profile_idx >= len(profiles):
            print("Invalid profile selection")
            return None
            
        profile = profiles[profile_idx]
        
        # Check SSO login if needed
        if not self.check_sso_login(profile):
            print(f"Failed to authenticate with profile '{profile}'")
            return None
            
        # Get SSM instances
        print(f"\nGetting instances managed by SSM for profile '{profile}'...")
        instances = self.get_ssm_instances(profile)
        
        if not instances:
            print("No instances managed by SSM found")
            return None
            
        # Ask for instance
        print("\nAvailable instances:")
        for i, instance in enumerate(instances):
            print(f"{i+1}. {instance['name']} ({instance['id']}) - {instance['ip']}")
            
        instance_idx = int(input("\nSelect instance (number): ")) - 1
        if instance_idx < 0 or instance_idx >= len(instances):
            print("Invalid instance selection")
            return None
            
        instance = instances[instance_idx]
        
        # Ask for remote host and ports
        remote_host = input("\nEnter remote host (IP or hostname): ")
        if not remote_host:
            print("Remote host cannot be empty")
            return None
            
        remote_port = input("Enter remote port: ")
        if not remote_port.isdigit():
            print("Remote port must be a number")
            return None
            
        local_port = input("Enter local port: ")
        if not local_port.isdigit():
            print("Local port must be a number")
            return None
            
        # Create connection object
        connection = {
            'profile': profile,
            'instance_id': instance['id'],
            'remote_host': remote_host,
            'remote_port': remote_port,
            'local_port': local_port,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save connection
        self.connections[name] = connection
        self.save_connections()
        
        return connection
        
    def list_connections(self):
        """List saved connections"""
        if not self.connections:
            print("No saved connections found")
            return []
            
        # Prepare table data
        table_data = []
        for name, conn in self.connections.items():
            table_data.append([
                name,
                conn['profile'],
                conn['instance_id'],
                f"{conn['remote_host']}:{conn['remote_port']}",
                conn['local_port'],
                conn['created_at']
            ])
            
        # Print table
        headers = ["Name", "Profile", "Instance ID", "Remote Host:Port", "Local Port", "Created At"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        return list(self.connections.keys())
        
    def delete_connection(self, name):
        """Delete a saved connection"""
        if name in self.connections:
            del self.connections[name]
            self.save_connections()
            print(f"Connection '{name}' deleted.")
        else:
            print(f"Connection '{name}' not found.")
            
    def change_password(self):
        """Change the password used to encrypt connections"""
        if not os.path.exists(self.connections_file):
            print("No hay conexiones guardadas. Crea una conexión primero.")
            return
            
        # Cargar conexiones con la contraseña actual
        try:
            old_key = self.get_encryption_key()
            fernet_old = Fernet(old_key)
            
            with open(self.connections_file, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = fernet_old.decrypt(encrypted_data)
            connections_data = decrypted_data.decode()
            
            # Solicitar y validar nueva contraseña
            new_password = getpass.getpass("Ingresa la nueva contraseña: ")
            if not new_password or new_password.strip() == "":
                print("Error: La contraseña no puede estar vacía")
                return
                
            confirm_password = getpass.getpass("Confirma la nueva contraseña: ")
            if new_password != confirm_password:
                print("Error: Las contraseñas no coinciden")
                return
                
            # Generar nuevo salt y clave
            new_salt = os.urandom(16)
            with open(self.key_file, 'wb') as f:
                f.write(new_salt)
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=new_salt,
                iterations=100000,
            )
            new_key = base64.urlsafe_b64encode(kdf.derive(new_password.encode()))
            fernet_new = Fernet(new_key)
            
            # Re-encriptar con la nueva clave
            new_encrypted_data = fernet_new.encrypt(connections_data.encode())
            
            with open(self.connections_file, 'wb') as f:
                f.write(new_encrypted_data)
                
            print("Contraseña cambiada exitosamente")
            
        except (InvalidToken, ValueError) as e:
            print("Error: Contraseña incorrecta. No se pudo cambiar la contraseña.")
        except Exception as e:
            print(f"Error al cambiar la contraseña: {e}")
            
    def main(self):
        """Main function to run the tool"""
        parser = argparse.ArgumentParser(description="AWS SSM Port Forwarding Manager")
        parser.add_argument('--new', action='store_true', help='Create a new connection')
        parser.add_argument('--list', action='store_true', help='List saved connections')
        parser.add_argument('--connect', metavar='NAME', help='Connect using a saved connection')
        parser.add_argument('--delete', metavar='NAME', help='Delete a saved connection')
        parser.add_argument('--change-password', action='store_true', help='Change the encryption password')
        
        args = parser.parse_args()
        
        # Load saved connections
        self.load_connections()
        
        if args.new:
            connection = self.create_new_connection()
            if connection:
                answer = input("Do you want to start this connection now? (y/n): ")
                if answer.lower() == 'y':
                    self.start_port_forwarding(connection)
        elif args.list:
            self.list_connections()
        elif args.delete:
            self.delete_connection(args.delete)
        elif args.connect:
            if args.connect in self.connections:
                self.start_port_forwarding(self.connections[args.connect])
            else:
                print(f"Connection '{args.connect}' not found.")
        elif args.change_password:
            self.change_password()
        else:
            # Interactive mode
            while True:
                print("\nAWS SSM Port Forwarding Manager")
                print("1. Create new connection")
                print("2. List saved connections")
                print("3. Connect using saved connection")
                print("4. Delete connection")
                print("5. Change password")
                print("6. Exit")
                
                choice = input("\nEnter your choice (1-6): ")
                
                if choice == '1':
                    connection = self.create_new_connection()
                    if connection:
                        answer = input("Do you want to start this connection now? (y/n): ")
                        if answer.lower() == 'y':
                            self.start_port_forwarding(connection)
                elif choice == '2':
                    self.list_connections()
                elif choice == '3':
                    connection_names = self.list_connections()
                    if connection_names:
                        name = input("\nEnter connection name to connect: ")
                        if name in self.connections:
                            self.start_port_forwarding(self.connections[name])
                        else:
                            print(f"Connection '{name}' not found.")
                elif choice == '4':
                    connection_names = self.list_connections()
                    if connection_names:
                        name = input("\nEnter connection name to delete: ")
                        self.delete_connection(name)
                elif choice == '5':
                    self.change_password()
                elif choice == '6':
                    break
                else:
                    print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        SSMPortForwarder().main()
    except KeyboardInterrupt:
        print("\nExiting...")
