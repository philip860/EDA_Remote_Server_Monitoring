import asyncio
import os
import asyncssh
from typing import Any, Dict

"""
ssh_file_check.py

Description:
An event-driven Ansible custom module that SSHs into a machine
and checks for the presence of a file.

Arguments:
  - delegate_to: Remote system to SSH into
  - username: SSH username
  - password: (optional) SSH password (if no SSH key)
  - private_key: (optional) Path to SSH private key
  - file_path: The file path to check for presence
  - interval: (optional) Time interval for polling (default: 10 sec)

Usage in a rulebook:
- name: Check file presence over SSH
  hosts: localhost
  sources:
    - my_custom_modules.ssh_file_check:
        delegate_to: example-server-2
        username: ansible
        private_key: /home/ansible/.ssh/id_rsa
        file_path: /var/log/system.log
        interval: 5
  rules:
    - name: File detected
      condition: event.found is true
      action:
        debug:
"""

async def check_file_exists(host: str, username: str, password: str, private_key: str, file_path: str) -> bool:
    """SSH into a remote host and check if a file exists."""
    try:
        conn_args = {"username": username}
        if password:
            conn_args["password"] = password
        if private_key:
            conn_args["client_keys"] = [private_key]

        async with asyncssh.connect(host, **conn_args) as conn:
            result = await conn.run(f"test -f {file_path} && echo FOUND || echo NOT_FOUND", check=True)
            return "FOUND" in result.stdout

    except (asyncssh.Error, Exception) as e:
        print(f"SSH connection failed: {e}")
        return False

async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    """Main event loop"""
    host = args.get("delegate_to")
    username = args.get("username")
    password = args.get("password")
    private_key = args.get("private_key")
    file_path = args.get("file_path")
    interval = int(args.get("interval", 10))

    if not all([host, username, file_path]):
        print("Missing required parameters: delegate_to, username, file_path")
        return

    while True:
        found = await check_file_exists(host, username, password, private_key, file_path)
        if found:
            await queue.put({"event": "file_found", "host": host, "file_path": file_path, "found": True})
        await asyncio.sleep(interval)

# Run directly for testing
if __name__ == "__main__":
    host = os.environ.get("SSH_HOST")
    username = os.environ.get("SSH_USERNAME")
    password = os.environ.get("SSH_PASSWORD")
    private_key = os.environ.get("SSH_PRIVATE_KEY")
    file_path = os.environ.get("SSH_FILE_PATH")

    class MockQueue:
        async def put(self, event):
            print(event)

    asyncio.run(main(MockQueue(), {
        "delegate_to": host,
        "username": username,
        "password": password,
        "private_key": private_key,
        "file_path": file_path,
    }))