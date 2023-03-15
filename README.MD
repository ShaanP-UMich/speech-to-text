Project inspiried by: https://www.youtube.com/watch?v=UY7sRB60wZ4&

To create the Python virtual environment run:

MacOS:
virtualenv -p python3.8 env

Windows users: User PowerShell (doesn't work natively through WSL2)

1. Create a Virtual Environment
    python3.8 -m venv env # Make sure you have Python 3.8 installed (can get from the Windows store)
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser # Run so you can activate the activate script
    .\env\Scripts\activate # Activate virtual env
2. Setup modules
    pip install -r requirements.txt
3. Install ffmpeg with choco
    choco install ffmpeg # (https://jcutrer.com/windows/install-chocolatey-choco-windows10)