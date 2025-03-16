from source import logger
from dotenv import load_dotenv
from source import create_app

#Loads dotEnv for testing
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)