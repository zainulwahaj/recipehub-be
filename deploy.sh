#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv git -y

# Clone your repo (replace with your repo URL)
git clone https://github.com/zainulwahaj/recipehub-be.git
cd recipehub-be

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (you'll need to edit this with your actual values)
cat > .env << EOF
DATABASE_URL=your_supabase_connection_string
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
EOF

echo "Edit .env file with your actual credentials: nano .env"
echo "Then run: source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
