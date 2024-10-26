# smoobu-to-google-calendar
This is a docker container that sync the customer data with google calendar

# Clone the repository
```bash
git clone https://github.com/mr-jz/smoobu-to-google-calendar.git
```
then change into the directory:
```bash
cd smoobu-to-google-calendar
```

# Setup

## Python packages setup
```bash
pip install -r requirements.txt
```

## Create the Google Calendar credentials
1. Go to the [Google API Console](https://console.developers.google.com/apis/dashboard)
2. Create a new project
3. Enable the Calendar API
4. Create OAuth Client ID
5. Download the credentials file under the name `calendar-secrets.json`

## Create the Google Calendar token
1. If you have your `calendar-secrets.json` you can run the following command to generate the token:
```bash
python generate_google_calendar_token.py
```

## Create the Smoobu API key
1. Go to the [Smoobu](https://login.smoobu.com/login)
2. Create an account
3. Go to the [API Keys](https://login.smoobu.com/api-keys) page
4. Create a new API key
5. Copy the API key

## Create the .setenv file
1. Copy the `.setenv.example` file to `.setenv`
2. Replace the `SMOOBU_API` and `TIME_ZONE` values with your Smoobu API key and time zone

## Run the container

To run the container use the following command:
```bash
docker compose up
```
If you want no outputs you can run the command with the `-d` flag:
```bash
docker compose up -d
```
This also allows you to just close the terminal and the container will continue running in the background.
