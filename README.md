URL Shortener with Analytics and Caching
This document provides a comprehensive overview of the URL Shortener project, detailing its objectives, architectural design, database schema, and a retrospective on the significant challenges encountered during development and their resolutions.

1. Project Objective
The primary objective of this project is to develop a robust and efficient URL shortening service. This service aims to:

Shorten Long URLs: Convert lengthy web addresses into concise, easy-to-share short codes.

Facilitate Redirection: Efficiently redirect users from the short URL to the original long URL.

Provide Basic Analytics: Track the number of clicks for each short URL.

Implement Caching: Utilize Redis to cache URL mappings for rapid redirection, reducing database load.

Ensure Scalability & Reliability: Leverage modern asynchronous frameworks (FastAPI) and containerization (Docker) for a scalable and maintainable architecture.

Prevent Abuse: Incorporate basic rate limiting on URL creation.

2. Project File Structure
The project follows a modular and organized structure, promoting separation of concerns and maintainability.

<img width="898" height="462" alt="image" src="https://github.com/user-attachments/assets/d6e9ec48-b966-4458-b8f5-aebc6a8af65b" />


3. Database Design Structure (PostgreSQL)
The project utilizes PostgreSQL to store URL mappings and click event data. The database schema is designed for simplicity and efficiency.
<img width="957" height="597" alt="image" src="https://github.com/user-attachments/assets/a209e56c-3730-4dca-a1cc-d67965f46552" />

<img width="344" height="647" alt="image" src="https://github.com/user-attachments/assets/fc9682d7-5fa7-4f41-a6db-fd72a0be91dc" />

4. Challenges Faced and Solutions
Developing this project involved several common but challenging issues, primarily related to Docker containerization, database connectivity, and asynchronous testing. Each challenge provided valuable learning opportunities.

Challenge 1: collected 0 items when running Pytest
Problem: Pytest was reporting "collected 0 items" even though test files were present.
Diagnosis: The rootdir shown by pytest was C:\url_shortner\app, indicating it was looking for tests in the wrong directory. Test files were correctly placed in C:\url_shortner\tests.
Solution: The user was running pytest from the wrong directory. The fix was to navigate to the project's root directory (C:\url_shortner) before executing pytest.

Challenge 2: asyncpg.exceptions.InvalidPasswordError: password authentication failed (Docker)
Problem: The FastAPI application failed to connect to the PostgreSQL database within Docker with a password authentication error, despite POSTGRES_USER and POSTGRES_PASSWORD being correctly set in docker-compose.yml.
Diagnosis: This typically occurs when the PostgreSQL data volume (postgres_data) was initialized in a previous run with different credentials (e.g., the default postgres user). Changing environment variables in docker-compose.yml doesn't alter an already initialized database's users.
Solution: A complete teardown of Docker containers and their associated volumes was required:
docker-compose down -v
docker-compose up --build -d
The -v flag is critical as it removes the persistent data volumes, forcing PostgreSQL to re-initialize with the correct credentials on the next startup. This was applied for both the main db and test db_test services when they encountered this error.

Challenge 3: Application startup failed. Exiting. (No Retry Messages)
Problem: The FastAPI application container was failing to start, but the logs didn't show the expected database connection retry messages, indicating the new retry logic wasn't active.
Diagnosis: Docker was using an old image of the app service. Code changes within the application's Python files are not automatically reflected in a running Docker container or its existing image.
Solution: The Docker image for the app service needed to be rebuilt.
docker-compose up --build -d
The --build flag forces Docker to rebuild the image from the Dockerfile, incorporating the latest app/database.py with the retry logic.

Challenge 4: socket.gaierror: [Errno 11001] getaddrinfo failed (Redis Timeout in Docker)
Problem: The FastAPI application (within Docker) failed to connect to the Redis container, showing a DNS resolution failure or network issue.
Diagnosis: This indicated that the app container was trying to connect to an incorrect Redis host (e.g., an external IP address) instead of the redis service name within the Docker network. This usually happens if REDIS_HOST was misconfigured in .env or docker-compose.yml.
Solution: Ensured REDIS_HOST: redis was correctly set in the environment section of the app service in docker-compose.yml. A clean docker-compose down -v followed by docker-compose up --build -d was performed to ensure the correct configuration was applied and network issues were cleared.

Challenge 5: The term 'redis-cli' is not recognized (Local Redis Setup on Windows)
Problem: When trying to test Redis locally on Windows, redis-cli and apt commands were not found.
Diagnosis: The user was attempting to run Linux-specific commands (sudo apt, redis-cli) in a Windows PowerShell terminal.
Solution: Guided the user to open the Ubuntu terminal (installed via WSL) and execute the Linux commands within that environment to install and manage Redis.

Challenge 6: ConnectionRefusedError: [Errno 10061] Connect call failed (Local FastAPI to Redis in VirtualBox VM)
Problem: The FastAPI application (running directly on Windows) could find the VirtualBox VM's IP address but was refused connection by Redis.
Diagnosis: This indicated that Redis inside the VM was either not listening on the VM's network interface (only on 127.0.0.1 by default) or the VM's firewall was blocking the connection.
Solution:
Modified Redis configuration (/etc/redis/redis.conf) inside the VM: Changed bind 127.0.0.1 ::1 to bind 0.0.0.0 (or the specific VM IP) and set protected-mode no (for development convenience).
Restarted Redis service in the VM.
Verified VM firewall (UFW): Ensured sudo ufw allow 6379/tcp was active.
Updated app/config.py (REDIS_HOST) to use the VM's actual IP address (172.25.41.139).

Challenge 7: "Click events db is empty" (Data not visible in PgAdmin)
Problem: Logs showed successful INSERT and COMMIT for click_events, but PgAdmin still showed the table as empty.
Diagnosis: The issue was not with the application or database, but with PgAdmin's display. It often caches table data or requires explicit refresh.
Solution: Provided precise instructions to:
Ensure connection to the correct database (url_shortener_db, port 5432).
Right-click on the click_events table in PgAdmin and select "Refresh".
Then, right-click again and select "View/Edit Data" -> "All Rows" to force a fresh query and display.

Conclusion
This URL Shortener project now stands as a fully functional backend application, capable of shortening URLs, redirecting users, and tracking basic analytics. The journey through various debugging scenarios, particularly around Docker networking, PostgreSQL authentication, Redis connectivity, and Python asynchronous patterns, has significantly reinforced the understanding of building robust, containerized microservices. The project is now well-positioned for further enhancements, such as a dedicated frontend UI, advanced analytics, and user management features.
