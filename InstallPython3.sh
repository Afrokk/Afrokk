sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10
# Enter whatever older version of Python3 you have in the line below
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1

# Sets Python3.10 as the default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2
echo "Now run 'sudo update-alternatives --config python3'"
