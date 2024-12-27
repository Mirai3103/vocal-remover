sudo apt-get update && sudo apt-get install ffmpeg libsm6 libxext6  -y
pip install -r requirements.txt

wget https://github.com/tsurumeso/vocal-remover/releases/download/v5.1.1/vocal-remover-v5.1.1.zip
unzip vocal-remover-v5.1.1.zip -d vocal-remover
cp vocal-remover/vocal-remover/models/baseline.pth ./models/baseline.pth
rm -rf vocal-remover
rm vocal-remover-v5.1.1.zip
