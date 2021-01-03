# When Utility Companies Don't Give You Access to Your Data

Getting current utility usage. In this case, demand power.

Run scripts in docker container with selenium and headless browser installed.

# Build and Run

From the main directory, use `docker-compose build` to build the local image. This will create an image named _utility-power:latest_.

Next, create a file named `.env` with the following contents:

```
UNITED_POWER_USERNAME=username_for_site
UNITED_POWER_PASSWORD=password_for_site
```

Finally, run the image via `docker-compose up`. Note that the first time it may fail as it takes a long time to retrieve the data. If it does fail you may need to do a `docker-compose down` to clear the network and resources used by the Chromium image.

## TODOs

1. Error checking for bad username/password - currently continues and waits for "My Consumption Data" link which will never occur.


