# launch_redis.py
import subprocess
import os
import sys

# Path to Redis binaries (adjust if needed)
REDIS_DIR = os.path.join(os.path.dirname(__file__), 'redis')
REDIS_SERVER = os.path.join(REDIS_DIR, 'redis-server.exe')
REDIS_CONF = os.path.join(REDIS_DIR, 'redis.windows.conf')

def start_redis():
    if not os.path.exists(REDIS_SERVER):
        print("[!] redis-server.exe not found.")
        sys.exit(1)

    print("[+] Launching Redis...")
    try:
        subprocess.Popen([REDIS_SERVER, REDIS_CONF], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] Redis launched successfully.")
    except Exception as e:
        print(f"[!] Failed to launch Redis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_redis()
