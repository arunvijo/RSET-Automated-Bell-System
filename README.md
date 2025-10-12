# RSET Automated Bell System

A robust, web-based system designed to automate bells, anthems, and announcements for Rajagiri School of Engineering and Technology. This project features a modern Django web interface for managing schedules and a resilient client-server architecture using a REST API, ensuring that client devices automatically recover after power failures.

---

## Overview

This project replaces a manual or outdated bell system with a fully automated, centrally managed solution. It is composed of two primary components:

1.  **Django Web Application:** A secure, modern web dashboard that allows authorized users to create, view, edit, and apply complex bell schedules (called "Profiles").
2.  **Client Scripts:** Lightweight Python scripts designed to run on low-cost hardware like a Raspberry Pi. These clients are placed in different physical locations (e.g., Main Block, KE Block) and are responsible for ringing the physical bells.

The core of the modernized system is its **resilience**. Client devices are "smart" and will automatically fetch their correct schedule from the central server upon startup or after a power outage, eliminating the need for manual intervention.

### Architectural Diagram

```

\+-----------------+      +----------------------+      +--------------------+
|  Administrator  | ---\> |  Django Web App      |      |  SQLite Database   |
| (Web Browser)   |      |  (Gunicorn + Nginx)  | \<--\> | (Stores Profiles)  |
\+-----------------+      +----------------------+      +--------------------+
|
| (Serves REST API)
|
\+-------------------+-------------------+
|                   |                   |
v                   v                   v
\+-----------------+   +-----------------+   +-----------------+
| Raspberry Pi    |   | Raspberry Pi    |   | Raspberry Pi    |
| (Main Block)    |   | (KE Block)      |   | (PG Block)      |
| [Pulls schedule |   | [Pulls schedule |   | [Pulls schedule |
|  on boot]       |   |  on boot]       |   |  on boot]       |
\+-----------------+   +-----------------+   +-----------------+

````

## Key Features

* **Modern Web Interface:** A clean, responsive, and mobile-friendly UI built with Bootstrap 5 for easy management of schedules.
* **Robust Database:** A normalized database schema that allows for unlimited bells per profile, ensuring scalability and maintainability.
* **Full CRUD Functionality:** Easily **C**reate, **R**ead, **U**pdate, and **D**elete bell profiles through the web interface.
* **Resilient REST API:** A secure API endpoint allows client devices to pull their schedules, making the system fault-tolerant and solving the power failure problem.
* **Automated Client Recovery:** Raspberry Pi clients automatically fetch their schedule on boot, eliminating the need for manual resets after a power outage.
* **Dynamic Scheduling:** The client scripts automatically generate `cron` jobs based on the schedule received from the server.
* **Hardware Control:** Includes scripts to control amplifiers via GPIO pins, turning them on before playing a sound and off afterward to save power.

---

## Technology Stack

* **Backend:** Django, Django REST Framework
* **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
* **Database:** SQLite (for development and small-scale production)
* **Client:** Python 3, `requests` library
* **Deployment:**
    * **Server:** Gunicorn (Application Server), Nginx (Web Server), `systemd` (Service Manager)
    * **Client (Raspberry Pi):** `cron` (Scheduler), `systemd`

---

## Getting Started

### 1. Server-Side (Django Application)

These steps are for setting up the main web application on a development machine or a production server.

**Prerequisites:** Python 3, `venv`

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/arunvijo/rset-automated-bell-system.git](https://github.com/arunvijo/rset-automated-bell-system.git)
    cd rset-automated-bell-system
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Perform initial database setup:**
    ```bash
    python manage.py makemigrations web
    python manage.py migrate
    python manage.py createsuperuser
    ```

5.  **Create initial data for active profiles:**
    * Run the server: `python manage.py runserver`
    * Go to the admin panel (`/admin/`) and log in.
    * Add one entry to each of the `Main_currents`, `Pg_currents`, and `Ke_currents` tables. You can name them "Default".

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

### 2. Client-Side (Raspberry Pi)

These steps are for setting up a Raspberry Pi device that will ring the bells.

**Prerequisites:** Raspberry Pi with Raspberry Pi OS, connected to the network.

1.  **Install necessary software:**
    ```bash
    sudo apt-get update
    sudo apt-get install git python3-pip mpg123
    pip3 install requests
    ```

2.  **Clone the repository:**
    ```bash
    git clone [https://github.com/arunvijo/rset-automated-bell-system.git](https://github.com/arunvijo/rset-automated-bell-system.git)
    cd rset-automated-bell-system
    ```

3.  **Configure the client:**
    * Open the client script for editing: `nano bell_project/client/client.py`
    * **Crucially, set the `MY_BLOCK_NAME` and `SERVER_IP` variables:**

        ```python
        # For the Main Block Pi:
        MY_BLOCK_NAME = "main" 
        SERVER_IP = "192.168.1.100" # <-- The static IP of your Django server

        # For the KE Block Pi:
        MY_BLOCK_NAME = "ke" 
        SERVER_IP = "192.168.1.100" # <-- The static IP of your Django server
        ```

4.  **Automate the client to run on boot:**
    * Create a `systemd` service file: `sudo nano /etc/systemd/system/bell-client.service`
    * Paste the following configuration, adjusting paths if necessary:

        ```ini
        [Unit]
        Description=RSET Bell Client
        After=network-online.target

        [Service]
        User=pi
        WorkingDirectory=/home/pi/rset-automated-bell-system/bell_project/client
        ExecStart=/usr/bin/python3 /home/pi/rset-automated-bell-system/bell_project/client/client.py

        [Install]
        WantedBy=multi-user.target
        ```
    * Enable and start the service:
        ```bash
        sudo systemctl enable bell-client
        sudo systemctl start bell-client
        ```

---

## Usage

1.  **Log In:** Access the web application via the server's IP address and log in with your superuser credentials.
2.  **Create a Profile:** Navigate to "Add New Profile". Give the profile a name (e.g., "Regular Weekday") and add as many bell entries as needed, setting the time, type, and active days for each.
3.  **View and Edit Profiles:** Go to "View Profiles" to see all schedules. You can click the "Edit" button to modify any existing profile.
4.  **Apply a Profile:** Navigate to "Apply Profile". From the dropdown menus, select which profile should be active for each block (Main, KE, PG) and click "Apply Changes".

The client devices will now automatically fetch and apply the correct schedule the next time they boot up.

````
