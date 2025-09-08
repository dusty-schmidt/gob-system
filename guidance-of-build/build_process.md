# GOB Build and Deployment Process

This document outlines the correct procedure for making changes to the GOB application, building a new Docker image, and deploying it to see the updates.

### The Core Concept: Volumes vs. Image Files

The primary source of confusion during development is the difference between files baked into a Docker image and files mounted via a volume.

1.  **Baked into the Image (`docker build`):**
    *   When you run `docker build`, the `COPY` command in the `Dockerfile` takes a snapshot of your local files and copies them *inside* the new image.
    *   The image becomes a self-contained package with all the code it needs to run.

2.  **Mounted as a Volume (`docker run -v`):**
    *   Using the `-v` flag (e.g., `-v /your/local/path:/a0`) tells Docker to ignore the corresponding folder inside the image and use your local folder instead.
    *   This is ideal for rapid development, as local file changes are reflected instantly in the container without rebuilding.

A common issue arises when you build a new image but run it with a volume mount. The volume's local files will always override the files baked into the image, so your changes won't appear.

---

### Standard Build & Deploy Workflow

Follow these steps to reliably update your containerized application.

#### Step 1: Make Your Code Changes

Edit your files locally in the `/home/ds/sambashare/GOB/general-operations-bots/` directory.

#### Step 2: Build the New Docker Image

Package your changes into a new, self-contained image. Run this command from the project's root directory (`/home/ds/sambashare/GOB/`).

```bash
docker build -f /home/ds/sambashare/GOB/general-operations-bots/DockerfileLocal -t new-image-name /home/ds/sambashare/GOB/general-operations-bots
```

*   **`-f ...`**: Specifies the exact `Dockerfile` to use.
*   **`-t new-image-name`**: Tags the image with a memorable name (e.g., `gob-v2`, `gob-latest`).
*   **Final Path**: This is the "build context"—the source directory for the build.

#### Step 3: Stop and Remove the Old Container

A container name must be unique. Before starting a new container, you must stop and remove the old one.

```bash
docker stop gob-agent-system
docker rm gob-agent-system
```

#### Step 4: Run the New Container (Without a Volume)

Start a new container from your newly built image. **Crucially, do not use the `-v` flag.** This forces the container to use the code you just baked into the image.

```bash
docker run -d --name gob-agent-system -p 5000:80 new-image-name
```

*   **`-d`**: Runs the container in detached mode (in the background).
*   **`--name ...`**: Assigns the standard name to the container.
*   **`-p 5000:80`**: Maps port 5000 on your local machine to port 80 inside the container.

#### Step 5: Clear Your Browser Cache

Browsers aggressively cache web assets (CSS, JavaScript, images). To ensure you see the latest changes:

*   **Best Method:** Open a new **Incognito/Private browser window**.
*   **Alternative:** Use the "Hard Refresh" feature (`Ctrl+Shift+R` or `Cmd+Shift+R`).
*   **Most Thorough:** Use your browser's developer tools to clear the cache and site data for `localhost`.
