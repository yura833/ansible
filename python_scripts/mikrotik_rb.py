import time
import paramiko
import socket


def get_input(prompt, validation=None):
    while True:
        user_input = input(prompt).strip()
        if validation and not validation(user_input):
            print("Invalid input. Please try again.")
        else:
            return user_input


host = get_input("Please enter your MikroTik IP address: ")
username = get_input("Please enter your MikroTik username: ")
password = get_input("Please enter your MikroTik password: ")


def mikrotik_ssh():
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password, timeout=20, look_for_keys=False)

        # Execute the command to print interfaces
        stdin, stdout, stderr = ssh_client.exec_command('interface print')
        time.sleep(2)  # Wait for the command to complete
        interfaces_output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            print(f"Error:\n{error}")
            ssh_client.close()
            return

        print(f"Interfaces Output:\n{interfaces_output}")

        lines = interfaces_output.splitlines()
        interface_names = []

        for line in lines:
            parts = line.split()
            for part in parts:
                if part.startswith("ether") and part[5:].isdigit():
                    interface_names.append(part)
                    break

        # Loop through each interface and set MTU
        for interface_name in interface_names:
            set_mtu_command = f'interface ethernet set [ find default-name={interface_name} ] l2mtu=2000 mtu=1800'
            print(f"Executing: {set_mtu_command}")
            stdin, stdout, stderr = ssh_client.exec_command(set_mtu_command)
            time.sleep(2)  # Wait for the command to complete
            output = stdout.read().decode()
            error = stderr.read().decode()

            if output:
                print(f"Output:\n{output}")
            if error:
                print(f"Error:\n{error}")

        # Create Bridge
        print("\nCreating Bridge, type 'n' or 'no' to stop.")
        while True:
            create_bridge = get_input("Would you like to create a new bridge? (yes/no): ",
                                      lambda x: x in ('yes', 'no', 'n'))
            if create_bridge in ('n', 'no'):
                break

            bridge_name = get_input("Please enter the bridge name: ")
            create_bridge_command = f'interface bridge add name={bridge_name} protocol-mode=none'
            print(f"Executing: {create_bridge_command}")
            stdin, stdout, stderr = ssh_client.exec_command(create_bridge_command)
            time.sleep(2)
            output = stdout.read().decode()
            error = stderr.read().decode()

            if output:
                print(f"Output:\n{output}")
            if error:
                print(f"Error:\n{error}")

        # Choose subinterface or EoIP tunnel, or both
        print("\nChoose subinterface or EoIP tunnel, you can also choose both.")
        user_choice = get_input("Type 's' for subinterface, 'e' for EoIP tunnel, or 'b' for both: ",
                                lambda x: x in ('s', 'e', 'b'))

        def create_eoip_tunnel():
            print("\nCreating EoIP Tunnel, type 'n' or 'no' to stop.")
            while True:
                create_tunnel = get_input("Would you like to create an EoIP tunnel? (yes/no): ",
                                          lambda x: x in ('yes', 'no', 'n'))
                if create_tunnel in ('n', 'no'):
                    break
                tunnel_name = get_input("Please enter the tunnel name: ")
                local_address = get_input("Please enter the local address: ")
                remote_address = get_input("Please enter the remote address: ")
                tunnel_id = get_input("Please enter the tunnel ID: ")
                create_tunnel_command = (
                    f'interface eoip add name={tunnel_name} local-address={local_address} '
                    f'remote-address={remote_address} tunnel-id={tunnel_id}'
                )
                print(f"Executing: {create_tunnel_command}")
                cmd_stdin, cmd_stdout, cmd_stderr = ssh_client.exec_command(create_tunnel_command)
                time.sleep(2)
                cmd_output = cmd_stdout.read().decode()
                cmd_error = cmd_stderr.read().decode()

                if cmd_output:
                    print(f"Output:\n{cmd_output}")
                if cmd_error:
                    print(f"Error:\n{cmd_error}")

        def create_subinterface():
            print("\nCreating subinterface, type 'n' or 'no' to stop.")
            while True:
                mik_subinterface = get_input("Would you like to create a subinterface? (yes/no): ",
                                             lambda x: x in ('yes', 'no', 'n'))
                if mik_subinterface in ('n', 'no'):
                    break
                subinterface_name = get_input("Please enter the subinterface name: ")
                sub_physical_name = get_input("Please enter the physical interface name: ")
                sub_vlan_id = get_input("Please enter the VLAN ID: ")
                create_subinterface_command = (
                    f'interface vlan add name={subinterface_name} interface={sub_physical_name} vlan-id={sub_vlan_id}'
                )
                print(f"Executing: {create_subinterface_command}")
                cmd_stdin, cmd_stdout, cmd_stderr = ssh_client.exec_command(create_subinterface_command)
                time.sleep(2)
                cmd_output = cmd_stdout.read().decode()
                cmd_error = cmd_stderr.read().decode()

                if cmd_output:
                    print(f"Output:\n{cmd_output}")
                if cmd_error:
                    print(f"Error:\n{cmd_error}")

        if user_choice == 'e':
            create_eoip_tunnel()
        elif user_choice == 's':
            create_subinterface()
        elif user_choice == 'b':
            create_eoip_tunnel()
            create_subinterface()

        ssh_client.close()

    except socket.gaierror:
        print("Address-related error: Name or service not known")
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials")
    except paramiko.SSHException as sshException:
        print(f"Unable to establish SSH connection: {sshException}")
    except socket.timeout:
        print("Connection timed out")
    except Exception as e:
        print(f"Exception in connecting: {e}")


if __name__ == "__main__":
    mikrotik_ssh()
    print("Done :))")
