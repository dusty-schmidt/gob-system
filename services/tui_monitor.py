import curses
import socket
import time
import threading

def check_port(port):
    """Checks if a port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main(stdscr):
    """Main function for the TUI."""
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    services = {
        "Grid Overwatch Bridge": 8051,
        "General Operations Bots": 50001,
    }

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = "GOB System Monitor"
        stdscr.addstr(0, width // 2 - len(title) // 2, title)

        # Services
        row = 2
        for name, port in services.items():
            status = "ONLINE" if check_port(port) else "OFFLINE"
            color = curses.color_pair(1) if status == "ONLINE" else curses.color_pair(2)
            stdscr.addstr(row, 1, f"{name}: ")
            stdscr.addstr(row, 30, status, color)
            row += 1

        # Footer
        footer = "Press 'q' to quit"
        stdscr.addstr(height - 1, 1, footer)

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
