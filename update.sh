#!/bin/sh

cd /root/

if [ -d ~/offsets ]; then
    rm -r ~/offsets
fi
if [ -d /www/pppwn ]; then
    rm -r /www/pppwn
fi
if [ -f /www/pppwn.html ]; then
    rm /www/pppwn.html
fi
if [ -f /www/cgi-bin/pw.cgi ]; then
    rm /www/cgi-bin/pw.cgi
fi
if [ -f ~/run.sh ]; then
    rm ~/run.sh
fi
if command -v pppwn > /dev/null 2>&1; then
    rm /usr/bin/pppwn
fi

if ! command -v unzip > /dev/null 2>&1; then
    opkg update
    opkg install unzip
fi

wget -O main.zip https://github.com/CodeInvers3/PPPwn_ow/archive/refs/heads/main.zip
unzip main.zip

cd PPPwn_ow-main

mv -f offsets ~/
mv -f www/pppwn /www
mv -f www/pppwn.html /www
mv -f www/cgi-bin/pw.cgi /www/cgi-bin
mv -f run.sh ~/

cd ..
rm -r PPPwn_ow-main main.zip

chmod +x /www/cgi-bin/pw.cgi

echo "Updated!"

exit 0