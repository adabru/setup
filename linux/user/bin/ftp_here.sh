echo -e "connect to ftp://192.168.178.XX:2121\n\n"
ip a s | grep "inet "
cat ~/setup/stupid-ftpd.conf
stupid-ftpd -f ~/setup/stupid-ftpd.conf
