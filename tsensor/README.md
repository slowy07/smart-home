## setup
image [raspbian](https://www.raspberrypi.org/software/operating-systems/) and use command ``sudo raspi-config``
- ``network options -> wifi``
- ``Boot Options -> Desktop / CLI -> Console Autologin``
- ``Intefacing Options -> SSH``
- ``Intefacing Options -> SPI``
- ``Intefacing Options -> I2C``

enable acces to the thermal over uv:
```bash
cd /tmp
git clone https://github.com/groupgets/libuvc
cd libuvc
mkdir build
cmake ..
make
sudo make install
sudo sh -c "echo 'SUBSYSTEMS==\"usb\", ATTRS{idVendor}==\"1e4e\", ATTRS{idProduct}==\"0100\", SYMLINK+=\"pt1\", GROUP=\"usb\", MODE=\"666\"' >> /etc/udev/rules.d/99-pt1.rules"
```

## install
```bash
cd

echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

sudo apt-get update
sudo apt-get install -y python3-venv python3-opencv
sudo apt-get install -y libedgetpu1-max python3-edgetpu
sudo apt-get install -y libatlas-base-dev libjasper-dev libhdf5-dev libqt4-dev
sudo apt-get install -y git

python3 -m venv venv
. venv/bin/activate
pip3 install --no-cache-dir tensorflow
pip3 install opencv-contrib-python
pip3 install numpy absl-py Pillow
pip3 install smbus2 bme680
pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl
```

```bash
git clone https://github.com/slowy07/smart-home.git
cd smart-home/tsensor
curl -O https://github.com/maxbbraun/thermal-face/releases/latest/download/thermal_face_automl_edge_fast_edgetpu.tflite
```

## running 
```bash
cd ~/tsensor
. venv/bin/activate
export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
export PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages
```