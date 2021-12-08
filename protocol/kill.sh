pid=$(ps ax | grep 'main.py' | grep -v grep | awk '{print $1}')

if [ "$pid" != "" ];
then
    echo "kill " ${pid}
    sudo kill -9 ${pid}
fi

pid=$(ps ax | grep 'top_level.py' | grep -v grep | awk '{print $1}')

if [ "$pid" != "" ];
then
    echo "kill " ${pid}
    sudo kill -9 ${pid}
fi

pid=$(ps ax | grep 'read_usb.sh' | grep -v grep | awk '{print $1}')

if [ "$pid" != "" ];
then
    echo "kill " ${pid}
    sudo kill -9 ${pid}
fi

pid=$(ps ax | grep 'write_usb.sh' | grep -v grep | awk '{print $1}')

if [ "$pid" != "" ];
then
    echo "kill " ${pid}
    sudo kill -9 ${pid}
fi




