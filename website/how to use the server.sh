cd var/www/website # go to directory where website is
sudo rm -rf website-but-bad/ # remove old website code
sudo git clone https://github.com/L-Bot-SBHS/website-but-bad.git # add new website code
jobs # find runing processes
kill %1 # stop the website
python3 website-but-bad/app.py & # run da code in da background
# then go to http://sr8137wxs02.win.sydneyboys-h.schools.nsw.edu.au:8000/

# pip3 install flask # to install the flask, for example
