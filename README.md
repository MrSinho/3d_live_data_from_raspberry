# Plot accelleration data from raspberry pi

## Install requirements on main machine:

Works on ```Python 3.7.9```

```python
pip install -r requirements.txt
```

## Install requirements on raspberry pi
```python
sudo raspi-config
```
```python
sudo apt-get install git build-essential python-dev
cd ~
git clone https://github.com/adafruit/Adafruit_Python_ADXL345.git
cd Adafruit_Python_ADXL345
sudo python setup.py install
```
