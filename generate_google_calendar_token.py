import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def generate_token():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    token_path = "token.pickle"
    creds_path = "calendar-secrets.json"

    # Ensure the secrets directory exists
    if not os.path.exists("secrets"):
        os.makedirs("secrets")

    # Load existing credentials if they exist
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # If there are no valid credentials, perform the OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if the client secrets file exists
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"Client secrets file not found at '{creds_path}'. Please provide your 'calendar-secrets.json' file."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials to the token.pickle file
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    print(f"Token has been successfully generated and saved to '{token_path}'.")

if __name__ == "__main__":
    generate_token()
