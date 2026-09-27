"""Connect selected Google Workspace services using a local Desktop OAuth client."""
import argparse
import json
from pathlib import Path
from google_workspace import GoogleWorkspace,SCOPES
from skill_runtime import data_dir

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials",required=True,help="Desktop OAuth client JSON downloaded from Google Cloud")
    parser.add_argument("--services",nargs="+",choices=list(SCOPES),default=["drive","sheets","docs","slides"])
    parser.add_argument("--data-dir",type=Path,default=data_dir())
    args=parser.parse_args()
    from google_auth_oauthlib.flow import InstalledAppFlow
    connector=GoogleWorkspace(args.data_dir)
    # Keep already granted services when adding another service to the same local connection.
    services=set(args.services)|set(connector.status()["services"])
    scopes=sorted({s for k in services for s in SCOPES[k]})
    flow=InstalledAppFlow.from_client_secrets_file(args.credentials,scopes)
    credentials=flow.run_local_server(host="127.0.0.1",port=0,access_type="offline",prompt="consent",timeout_seconds=180)
    connector.save(credentials.to_json())
    print("Connected Google services: "+", ".join(sorted(services))+". Refresh Connections in Atlas.")

if __name__=="__main__": main()
