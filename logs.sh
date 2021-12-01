port=$(ps ax | grep 'python' | grep -v grep | awk '{print $1}')
echo $port
strace -p$port -s9999 -e write
