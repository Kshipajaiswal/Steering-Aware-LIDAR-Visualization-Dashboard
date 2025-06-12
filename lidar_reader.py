import socket
import struct
import threading
import requests
import time


IP_ADDRESS = "169.254.83.33"
scan_data = []

def parse_points(data):
    if len(data) < 77:
        print("Incomplete packet received")
        return []

    packets = {}
    points1 = []
    points2 = []

    # First packet header
    packets["magic"] = struct.unpack_from('<H', data, 0)[0]
    if packets["magic"] != 41564:
        print("Invalid magic number. Skipping packet.")
        return []

    packets["packettype"] = struct.unpack_from('<H', data, 2)[0]
    packets["packet_size"] = struct.unpack_from('<I', data, 4)[0]
    packets["header_size"] = struct.unpack_from('<H', data, 8)[0]
    packets["scan_number"] = struct.unpack_from('<H', data, 10)[0]
    packets["packet_number"] = struct.unpack_from('<H', data, 12)[0]
    packets["timestamp_raw"] = struct.unpack_from('<Q', data, 14)[0]
    packets["reserved"] = struct.unpack_from('<Q', data, 22)[0]
    packets["status_flags"] = struct.unpack_from('<I', data, 30)[0]
    packets["scan_frequency"] = struct.unpack_from('<I', data, 34)[0]
    packets["num_points_scan"] = struct.unpack_from('<H', data, 38)[0]
    packets["num_points_packet"] = struct.unpack_from('<H', data, 40)[0]
    packets["first_index"] = struct.unpack_from('<H', data, 42)[0]
    packets["first_angle"] = struct.unpack_from('<i', data, 44)[0]
    packets["angular_increment"] = struct.unpack_from('<i', data, 48)[0]
    packets["iq_input"] = struct.unpack_from('<I', data, 52)[0]
    packets["iq_overload"] = struct.unpack_from('<I', data, 56)[0]
    packets["iq_timestamp_raw"] = struct.unpack_from('<Q', data, 60)[0]
    packets["reserved2"] = struct.unpack_from('<Q', data, 68)[0]
    packets["header_padding"] = struct.unpack_from('<B', data, 76)[0]

    offset = packets["header_size"]
    for i in range(packets["num_points_packet"]):
        angle = (packets["first_angle"] + i * packets["angular_increment"]) / 10000.0 % 360
        distance = struct.unpack_from('<I', data, offset)[0]
        intensity = struct.unpack_from('<H', data, offset + 4)[0]
        points1.append([angle, distance, intensity])
        offset += 6

    # Check if second packet is present
    if len(data) < packets["packet_size"] + 77:
        print("Second packet not fully received. Returning partial points.")
        return points1

    offset2 = packets["packet_size"]
    packets["magic2"] = struct.unpack_from('<H', data, offset2 + 0)[0]
    if packets["magic2"] != 41564:
        print("Second packet magic number invalid. Returning first packet points only.")
        return points1

    packets["packettype2"] = struct.unpack_from('<H', data, offset2 + 2)[0]
    packets["packet_size2"] = struct.unpack_from('<I', data, offset2 + 4)[0]
    packets["header_size2"] = struct.unpack_from('<H', data, offset2 + 8)[0]
    packets["scan_number2"] = struct.unpack_from('<H', data, offset2 + 10)[0]
    packets["packet_number2"] = struct.unpack_from('<H', data, offset2 + 12)[0]
    packets["timestamp_raw2"] = struct.unpack_from('<Q', data, offset2 + 14)[0]
    packets["reserved3"] = struct.unpack_from('<Q', data, offset2 + 22)[0]
    packets["status_flags2"] = struct.unpack_from('<I', data, offset2 + 30)[0]
    packets["scan_frequency2"] = struct.unpack_from('<I', data, offset2 + 34)[0]
    packets["num_points_scan2"] = struct.unpack_from('<H', data, offset2 + 38)[0]
    packets["num_points_packet2"] = struct.unpack_from('<H', data, offset2 + 40)[0]
    packets["first_index2"] = struct.unpack_from('<H', data, offset2 + 42)[0]
    packets["first_angle2"] = struct.unpack_from('<i', data, offset2 + 44)[0]
    packets["angular_increment2"] = struct.unpack_from('<i', data, offset2 + 48)[0]
    packets["iq_input2"] = struct.unpack_from('<I', data, offset2 + 52)[0]
    packets["iq_overload2"] = struct.unpack_from('<I', data, offset2 + 56)[0]
    packets["iq_timestamp_raw2"] = struct.unpack_from('<Q', data, offset2 + 60)[0]
    packets["reserved4"] = struct.unpack_from('<Q', data, offset2 + 68)[0]
    packets["header_padding2"] = struct.unpack_from('<B', data, offset2 + 76)[0]

    offset = offset2 + packets["header_size2"]
    for i in range(packets["num_points_packet2"]):
        angle = (packets["first_angle2"] + i * packets["angular_increment2"]) / 10000.0
        angle = angle % 360 + 220  # Offset for second scan
        distance = struct.unpack_from('<I', data, offset)[0]
        intensity = struct.unpack_from('<H', data, offset + 4)[0]
        points2.append([angle, distance, intensity])
        offset += 6

    return points1 + points2

def get_car_steering_angle(scan_data, safe_distance=1000):
    """
    Decide steering angle based on obstacles in key sectors:
    - Front center (350–10° or -10–10°): stop or slow down
    - Front-left (~315° or -45°) and front-right (45°)
    Returns: angle in degrees (negative = left turn, positive = right turn)
    """

    front_obstacles = [d for a, d, _ in scan_data if -10 <= a <= 10 and d < safe_distance]
    right_obstacles = [d for a, d, _ in scan_data if 40 <= a <= 50 and d < safe_distance]
    left_obstacles = [d for a, d, _ in scan_data if 310 <= a <= 320 and d < safe_distance]

    if front_obstacles:
        if left_obstacles and right_obstacles:
            return 0  # both sides blocked, maybe stop or reverse
        elif left_obstacles:
            return 45  # turn right
        elif right_obstacles:
            return -45  # turn left
        else:
            return -30  # default turn left
    return 0  # path clear



def start_lidar_thread():
    def watchdog_guard(handle):
        """Keep refreshing the watchdog to avoid timeout."""
        while True:
            try:
                requests.get(f"http://{IP_ADDRESS}/cmd/refresh_handle?handle={handle}")
                time.sleep(5)  # Refresh every 5 seconds
            except:
                break  # Exit if the main thread likely failed

    def lidar_worker():
        global scan_data
        while True:
            try:
                response = requests.get(
                    f"http://{IP_ADDRESS}/cmd/request_handle_tcp?packet_type=B&watchdogtimeout=10000&start_angle=0").json()
                port = response['port']
                handle = response['handle']

                # Start scan output
                requests.get(f"http://{IP_ADDRESS}/cmd/start_scanoutput?handle={handle}")

                # Start watchdog refresher thread
                watchdog_thread = threading.Thread(target=watchdog_guard, args=(handle,), daemon=True)
                watchdog_thread.start()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((IP_ADDRESS, port))

                buffer = b""
                MAGIC = 41564
                HEADER_SIZE = 77

                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        raise ConnectionError("Disconnected from LIDAR.")
                    buffer += chunk

                    while len(buffer) >= HEADER_SIZE:
                        if struct.unpack_from('<H', buffer, 0)[0] != MAGIC:
                            buffer = buffer[1:]
                            continue

                        if len(buffer) < 6:
                            break

                        packet_size = struct.unpack_from('<I', buffer, 4)[0]
                        total_len = packet_size

                        if len(buffer) >= total_len + HEADER_SIZE:
                            if struct.unpack_from('<H', buffer, total_len)[0] == MAGIC:
                                total_len += struct.unpack_from('<I', buffer, total_len + 4)[0]

                        if len(buffer) < total_len:
                            break

                        packet_data = buffer[:total_len]
                        buffer = buffer[total_len:]

                        points = parse_points(packet_data)
                        if points:
                            scan_data = points

            except Exception as e:
                print(f"Error in lidar_worker: {e}")
            finally:
                try:
                    sock.close()
                    requests.get(f"http://{IP_ADDRESS}/cmd/stop_scanoutput?handle={handle}")
                    requests.get(f"http://{IP_ADDRESS}/cmd/release_handle?handle={handle}")
                except:
                    pass

            print("Restarting connection in 2 seconds...")
            time.sleep(2)  # Wait before retrying

    thread = threading.Thread(target=lidar_worker, daemon=True)
    thread.start()


def get_latest_scan_data():
    return scan_data