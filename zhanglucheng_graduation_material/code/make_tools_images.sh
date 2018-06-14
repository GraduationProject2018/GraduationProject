#!/bin/bash

# docker run -itd --privileged=true --name test kongkongkkk/language_images /usr/sbin/init
# docker exec -it test /bin/bash

yum -y install openssh-server
sed -i "s/#RSAAuthentication yes/RSAAuthentication yes/g"
sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" 
sed -i "s/#PermitRootLogin yes/PermitRootLogin yes/g" 

systemctl restart sshd.service
chkconfig sshd on

# docker commit -m"create tools bases" -a"kongkongkkk" test kongkongkkk/tools_images
# docker pull kongkongkkk/tools_images